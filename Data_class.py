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

        data_folder = "data"
        if __debug__:
            data_folder = "debug_" + data_folder
        
        self.input_folder   = os.path.join(data_folder, "input")
        self.archive_folder = os.path.join(data_folder, "archive")
        self.data_filepath  = os.path.join(data_folder, "logs")
        self.backup_folder  = os.path.join(data_folder, "backup")

        # Command lists
        self.commands = {"fetch"    : self.fetch_new_logs,
                         "list"     : self.print_all}

        debug_commands = {"ssl"     : self.copy_files_to_local,
                          "restore" : self.debug_restore_to_input,
                          "import"  : self.read_data}
        if __debug__:
            self.commands["debug"] = debug_commands

        print("Working directory:", os.path.abspath(data_folder), "\n")
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
        date = dt.datetime.today().strftime('%y%m%d_%H,%M')

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
            return # Return nothing to exit function
        
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

    # Instead of fetching from ssl we can load from archive
    def debug_restore_to_input(self):
        filename = os.listdir(self.archive_folder)[0]

        # remove contents of input folder
        if os.path.exists(self.input_folder) and os.path.isdir(self.input_folder):
            shutil.rmtree(self.input_folder)

        # move to input folder, this automatically renames folder as well
        copy_from = os.path.join(self.archive_folder, filename)
        shutil.copytree(copy_from, self.input_folder)

        if os.path.exists(self.input_folder) and os.path.isdir(self.input_folder):
            shutil.rmtree(self.input_folder)

    def read_data(self):
        new_log = Log(self.input_folder, self.general_log_filename)

        # Rename folder to timestamp
        timestamp = new_log.return_timestamp()
        new_name = str(timestamp).replace(":",";")
        new_path = os.path.join(self.archive_folder, new_name)

        # Check if log already archived
        if os.path.exists(new_path):# TODO Check if in array
            user_acknowledge("Logs already imported, please delete input folder as that is not done automatically")
            return
        
        # Rename and move
        os.rename(self.input_folder, new_name)
        shutil.move(new_name, self.archive_folder)

        # Add to file and save
        self.data.append(new_log)
        self.saveFile()

    # copies files to local, creates new log object, archives logs
    def fetch_new_logs(self):
        self.copy_files_to_local()
        self.read_data()
        

#%% Print data
    def print_all(self):
        grid = []
        headers = ["ID", "Time", "LIVE_FEED", "RECORDING_FOLDER"]
        for log_object in self.data:
            general_log = log_object.return_attributes()
            line = []
            for attribute in headers:
                try:
                    line.append(general_log[attribute])
                except:
                    line.append("")
            grid.append(line)
        print(tabulate(grid, headers, tablefmt='rounded_grid'))