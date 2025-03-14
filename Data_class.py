#%% Standard modules
import pickle
import datetime as dt
import paramiko
import os
from tqdm import tqdm
import shutil
import datetime as dt
import subprocess

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
        
        self.local_input    = os.path.join(self.data_folder, "input")
        self.archive_folder = os.path.join(self.data_folder, "archive")
        self.data_filename  = os.path.join(self.data_folder, "logs")
        self.backup_folder  = os.path.join(self.data_folder, "backup")

        # Command lists
        self.commands = {"fetch"    : self.fetch_new_logs}

        debug_commands = {"ssl"     : self.copy_files_to_local,
                          "restore" : self.debug_restore,
                          "import"  : self.debug_import,
                          "save"    : self.saveFile}
        if __debug__:
            self.commands["debug"] = debug_commands

        # Open file, this also creates a backup
        self.openFile()
            
        print(f"{len(self.data)} logs imported\n")

    def returnCommands(self):
        return self.commands
    
#%% Open and close file
    def openFile(self):
        try:
            with open(self.data_filename, 'rb') as file:
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
            os.rename(self.data_filename, date)

            # Move input to backup folder
            shutil.move(date, self.backup_folder)
        except: pass

        with open(self.data_filename, 'wb') as file:
            pickle.dump(self.data, file)

    # Copy files from ssh to local folder
    def copy_files_to_local(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        wifi = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
        wifi_data = wifi.decode('utf-8')
        if not "ROStig" in wifi_data:
            print("Not connected to ROStig WiFi!")
            return 0

        try:
            print("Connecting...")
            ssh.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_pwd)
            print("Success!")

            sftp = ssh.open_sftp()

            # Ensure local folder exists
            os.makedirs(self.local_input, exist_ok=True)

            # List files in the remote directory
            remote_files = sftp.listdir(self.ssh_folder)

            if not remote_files:
                print("No log files found")

            for log_file in tqdm(remote_files, desc="Downloading Logs"):
                remote_path = os.path.join(self.ssh_folder, log_file)
                local_path = os.path.join(self.local_input, log_file)
                sftp.get(remote_path, local_path)

            sftp.close()
        
        except paramiko.AuthenticationException:
            print("Authentication failed! Check credentials and SSH config.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            ssh.close()

    # Instead of fetching from ssl we can load from archive
    def debug_restore(self):
        filename = os.listdir(self.archive_folder)[0]
        shutil.rmtree(self.local_input)
        shutil.move(filename, self.local_input)
    
    # Creates new object with files in input folder
    def debug_import(self):
        new_log = Log(self.local_input, self.general_log_filename)
        self.data.append(new_log)

    # Move contents from input to archive with timestamp as name
    def archive_logs(self, new_name):

        # Ensure local folder exists
        os.makedirs(self.archive_folder, exist_ok=True)

        # Rename folder
        os.rename(self.local_input, new_name)

        # Move input to archive
        shutil.move(new_name, self.archive_folder)

    # copies files to local, creates new log object, archives logs
    def fetch_new_logs(self):
        self.copy_files_to_local()
        new_log = Log(self.local_input, self.general_log_filename)
        folder_name = new_log.return_folder_name()

        try:
            self.archive_logs(folder_name)
            self.data.append(new_log)
            self.saveFile()

        # If file already exists, print this and do not save
        except Exception as e:
            print(f"An unexpected error occurred: {e}")