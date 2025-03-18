#%% Standard modules
import pickle
import datetime as dt
import paramiko
import os
from tqdm import tqdm
import shutil
import datetime as dt
import subprocess
from tabulate import tabulate

#%% Custom modules
from functions import user_acknowledge
from functions import input_number
from functions import tabulate_dict

#%% Classes
from Log_class import Log


class Data:

    def __init__(self):
        if __debug__:
            print("\nDebug mode\n")

        # Init variables
        self.ssh_host   = "192.168.50.205"
        self.ssh_user   = "gulliview"
        self.ssh_pwd    = "Chalmers"
        self.ssh_folder = "/home/gulliview/advanced_mobility_model/build/output/"

        self.general_log_filename = "general.log"
        
        self.data_folder = "data"
        if __debug__:
            self.data_folder = "debug_" + self.data_folder
            self.debug_backup   = "manual_copy_logs"
        
        filepath = os.path.realpath(__file__)
        folderpath = os.path.dirname(filepath)
        self.data_folder = os.path.join(folderpath, self.data_folder)

        self.input_folder   = os.path.join(self.data_folder, "input")
        self.archive_folder = os.path.join(self.data_folder, "archive")
        self.data_filepath  = os.path.join(self.data_folder, "logs")
        self.backup_folder  = os.path.join(self.data_folder, "backup")

        # Command lists
        self.commands = {"fetch"    : self.fetch_new_logs,
                         "list"     : self.display_data}

        debug_commands = {"ssl"     : self.copy_files_to_local,
                          "import"  : self.read_data,
                          "fetch"   : self.fetch_from_debug_backup}
        if __debug__:
            self.commands["debug"] = debug_commands

        print("Working directory:", os.path.abspath(self.data_folder), "\n")
        # Open file, this also creates a backup
        self.openFile()
            
        print(f"{len(self.data)} logs imported\n")

    def returnCommands(self):
        return self.commands

#%% Data handling
    # Open and close file
    def openFile(self):
        try:
            with open(self.data_filepath, 'rb') as file:
                self.data = pickle.load(file)
        except:
            # If file could not be read, create new
            if input("Could not read file, create new? (y/n): ") == "y":
                self.data = []
                self.saveFile()
                print("\n")
            else: 
                raise SystemExit()
    def saveFile(self):
        
        # Filepath for backup
        date = dt.datetime.today().strftime('%y-%m-%d_%H;%M;%S')

        # Ensure backup folder exists
        os.makedirs(self.backup_folder, exist_ok=True)
        
        try:
            # Rename folder
            os.rename(self.data_filepath, date)

            # Move input to backup folder
            shutil.move(date, self.backup_folder)
        except: pass

        with open(self.data_filepath, 'wb') as file:
            pickle.dump(self.data, file)

    # Copy files from ssh to local folder
    def copy_files_to_local(self):
        
        # Checks if connected to right network
        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        wifi_data = wifi.decode('utf-8')
        
        if not "ROStig" in wifi_data:
            user_acknowledge("Not connected to ROStig WiFi!")
            return True # Return True to exit callin function as well
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print("Connecting...")
            ssh.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_pwd)
            print("Success!")

            sftp = ssh.open_sftp()

            # Ensure local folder exists
            os.makedirs(self.input_folder, exist_ok=True)

            # List files in the remote directory
            remote_files = sftp.listdir(self.ssh_folder)

            if not remote_files:
                print("No log files found")

            for log_file in tqdm(remote_files, desc="Downloading Logs"):
                remote_path = os.path.join(self.ssh_folder, log_file)
                local_path = os.path.join(self.input_folder, log_file)
                sftp.get(remote_path, local_path)

            sftp.close()
        
        except paramiko.AuthenticationException:
            print("Authentication failed! Check credentials and SSH config.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            ssh.close()

    # Import log data
    def read_data(self):
        if not os.path.exists(self.input_folder):
            user_acknowledge("Input folder not found, this message should only be present in debug mode")
            return
        
        new_log = Log(self.input_folder, self.general_log_filename)

        # Get new folder name, it's path and it's archive path to be moved to
        new_name = new_log.return_folder_name()
        new_input_path = os.path.join(self.data_folder, new_name)
        new_archive_path = os.path.join(self.archive_folder, new_name)

        # Check for timestamp in all imported logs
        exists_flag = False
        for log_object in self.data:
            if log_object.return_folder_name() == new_name:
                exists_flag = True

        # Check if log already archived
        if exists_flag or os.path.exists(new_archive_path):
            user_acknowledge("Logs already imported, please delete input folder as this cannot be done by the program")
            return

        # Rename and move
        os.rename(self.input_folder, new_input_path)
        shutil.move(new_input_path, new_archive_path)

        # Add to file and save
        self.data.append(new_log)
        self.saveFile()

    # copies files to local, creates new log object, archives logs
    def fetch_new_logs(self):
        if self.copy_files_to_local():
            return
        self.read_data()

    # copies logs from debug_backup folder to test everything when ssl not available
    def fetch_from_debug_backup(self):
        shutil.copytree(self.debug_backup, self.input_folder)
        self.read_data()

#%% Print data

    def print_all(self):
        grid = []
        headers = ["ID", "TIME", "VERSION", "COMMENT", "LIVE_FEED", "RECORDING_FOLDER"]
        for i,log_object in enumerate(self.data):

            general_log = log_object.return_attributes()

            # Add id to first index in output list
            line = [i+1]

            # Adds data to list except ID
            for attribute in headers[1:]:

                # If attribute exists and is in string, concatinate, elif just add it, else add empty string
                if attribute in general_log.keys() and type(general_log[attribute]) == type(""):
                    line.append(general_log[attribute][:30])
                elif attribute in general_log.keys():
                    line.append(general_log[attribute])
                else:
                    line.append("")
                    
            grid.append(line)
        
        print(tabulate(grid, headers, tablefmt='rounded_grid'))

    def display_data(self):
        self.print_all()

        # If there are no logs return
        if len(self.data) == 0:
            return
        
        # Get ID for log to view
        prompt = "Input ID of log you wish to view: "
        ID = input_number(len(self.data), prompt)
        if not ID:
            return
        
        # Get attributes if log with inputted ID and print
        attributes = self.data[ID-1].return_attributes()
        print(tabulate_dict(attributes, ["Type", "Value"]))

        self.data[ID-1].box_plot_all()