import os
import re
import paramiko
import matplotlib.pyplot as plt
from tqdm import tqdm
import shutil

def fetch_files(ssh_host, ssh_user, ssh_password, remote_folder, local_folder):
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

    except paramiko.AuthenticationException:
        print("Authentication failed! Check credentials and SSH config.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

def get_general(general_log_path):
    data = {}
    with open(general_log_path, "r", encoding="utf-8") as file:
        for line in file:
            if ':' in line:
                key, value = line.strip().split(":", 1)
                data[key.strip()] = value.strip()
    return data

if __name__ == "__main__":
    ssh_host = "192.168.50.205"
    ssh_user = "gulliview"
    ssh_password = "Chalmers"
    remote_folder = "/home/gulliview/advanced_mobility_model/build/output/"
    local_folder = "input"

    # fetch_files(ssh_host, ssh_user, ssh_password, remote_folder, local_folder)
    
    # Debug to fetch only from backup not from ssh
    # shutil.copytree("backup", "input")
    
    general_filename = "general.log"
    print("Reading " + general_filename)
    general_log_path = os.path.join(local_folder, general_filename)
    general_log = get_general(general_log_path)