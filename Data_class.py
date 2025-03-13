#%% Standard modules
import pickle
import datetime as dt
import paramiko


class Data:

    def __init__(self):
        self.ssh_host = "192.168.50.205"
        self.ssh_user = "gulliview"
        self.ssh_password = "Chalmers"
        self.remote_folder = "/home/gulliview/advanced_mobility_model/build/output/"
        self.local_folder = "input"

        self.commands = {"fetch"     : self.fetch_files}
    

#%% Open and close file
    def openFile(self):
        try:
            with open(self.local_folder, 'rb') as file:
                self.data = pickle.load(file)
        except:
            if input("Could not read file, create new? (y/n): ") == "y":
                self.data = []
                self.saveFile()
                print("\n")
            else: 
                raise SystemExit()
        
        
        
    def saveFile(self):
        
        filepath = self.filepath

        folderPath = filepath[ : filepath.rfind("/") + 1]
        filename = filepath[filepath.rfind("/") + 1 : ]
        date = dt.datetime.today().strftime('%y%m%d_%H,%M')
        backupFilepath = folderPath + "backup/" + filename + "_" + date
        
        try:
            with open(filepath, 'rb') as file:
                with open(backupFilepath, 'wb') as backupFile:
                    pickle.dump(pickle.load(file), backupFile)
        except: pass
        with open(filepath, 'wb') as file:
            pickle.dump(self.data, file)

    # Fetch from ssh
    def fetch_files(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # TODO: Remove old folder

        print("Connecting")
        try:
            ssh.connect(ssh_host, username=ssh_user, password=ssh_password)

            sftp = ssh.open_sftp()
            os.makedirs(local_folder, exist_ok=True)  # Ensure local folder exists

            # List files in the remote directory
            remote_files = sftp.listdir(remote_folder)

            if not remote_files:
                print("No log files found")

            for log_file in tqdm(remote_files, desc="Downloading Logs"):
                remote_path = os.path.join(remote_folder, log_file)
                local_path = os.path.join(local_folder, log_file)
                sftp.get(remote_path, local_path)

            sftp.close()