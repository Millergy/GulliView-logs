#%% Standard modules
import pickle
import datetime as dt
import paramiko
import os
from tqdm import tqdm
import time

class Data:

    def __init__(self):
        self.ssh_host = "192.168.50.205"
        self.ssh_user = "gulliview"
        self.ssh_password = "Chalmers"
        self.remote_folder = "/home/gulliview/advanced_mobility_model/build/output/"
        self.local_folder = "input"
        self.filename = "data"
        self.general_filename = "general.log"

        self.openFile()

        self.commands = {"fetch"    : self.fetch_files,
                         "import"   : self.text_to_dict}

        if __debug__:
            print("Debug\n")

            self.commands = {"fetch"    : self.fetch_files,
                         "import"   : self.text_to_dict}

        else:
            self.commands = {"fetch"    : self.fetch_files}

            
        # print(f"{len(self.logs)} logs imported\n")

    def returnCommands(self):
        return self.commands
    
#%% Open and close file
    def openFile(self):
        try:
            with open(self.filename, 'rb') as file:
                self.data = pickle.load(file)
        except:
            if input("Could not read file, create new? (y/n): ") == "y":
                self.data = []
                self.saveFile()
                print("\n")
            else: 
                raise SystemExit()
        
    def saveFile(self):

        folderPath = "backup/"
        date = dt.datetime.today().strftime('%y%m%d_%H,%M')
        backupFilepath = os.path.join(folderPath, self.filename + "_" + date)

        os.makedirs(backupFilepath, exist_ok=True)  # Ensure local folder exists
        
        try:
            with open(self.filename, 'rb') as file:
                with open(backupFilepath, 'wb') as backupFile:
                    pickle.dump(pickle.load(file), backupFile)
        except: pass
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    # Fetch from ssh
    def fetch_files(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # TODO: Backup old folder

        print("Connecting...")
        try:
            ssh.connect(self.ssh_host, username=self.ssh_user, password=self.ssh_password)

            sftp = ssh.open_sftp()
            os.makedirs(self.local_folder, exist_ok=True)  # Ensure local folder exists

            # List files in the remote directory
            remote_files = sftp.listdir(self.remote_folder)

            if not remote_files:
                print("No log files found")

            for log_file in tqdm(remote_files, desc="Downloading Logs"):
                remote_path = os.path.join(self.remote_folder, log_file)
                local_path = os.path.join(self.local_folder, log_file)
                sftp.get(remote_path, local_path)

            sftp.close()
        
        except paramiko.AuthenticationException:
            print("Authentication failed! Check credentials and SSH config.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            ssh.close()



    def text_to_dict(self):

        # Init dict
        data = {}
        other = {}

        # Go through all files in folder
        for log_filename in tqdm(os.listdir(self.local_folder), desc="Importing data"):
            log_filepath = os.path.join(self.local_folder, log_filename)

            # Init dict for logs, 'other' is for general log outputs, used to debug functionality
            data[log_filename] = {}
            other[log_filename] = []

            with open(log_filepath, "r", encoding="utf-8") as file:
                for line in file:

                    # ':' represents data, otherwise it is just info and is put in 'other'
                    if ':' in line:

                        # Groub data by key, the key is the string before the first ':'
                        # For every key ther is a list with the values
                        key, value = line.strip().split(":", 1)
                        data[log_filename].setdefault(key, []).append(value.strip())

                    elif not line in other[log_filename]:
                        other[log_filename].append(line)

        return data, other