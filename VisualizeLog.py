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

def parse_log_file(log_content):
    loops = []
    remap_times = []
    transform_times = []
    durations = []
    
    loop_pattern = re.compile(r"Loop (\d+): trial=\d+, Duration=(\d+) us")
    remap_pattern = re.compile(r"Remap: ([\d\.]+) ms")
    transform_pattern = re.compile(r"Transform color: ([\d\.]+) ms")
    
    lines = log_content.splitlines()
    i = 0
    
    loops, remap_times, transform_times, durations = [], [], [], []

    # Wrap your loop with tqdm to display progress
    for _ in tqdm(range(len(lines)), desc="Processing Lines"):
        remap_time = transform_time = duration = None

        while i < len(lines) and not lines[i].startswith("Loop"):
            remap_match = remap_pattern.search(lines[i])
            transform_match = transform_pattern.search(lines[i])

            if remap_match:
                remap_time = float(remap_match.group(1))
            if transform_match:
                transform_time = float(transform_match.group(1))

            i += 1

        if i < len(lines) and lines[i].startswith("Loop"):
            loop_match = loop_pattern.search(lines[i])
            if loop_match:
                loop = int(loop_match.group(1))
                duration = int(loop_match.group(2)) / 1000.0  # Convert us to ms

                loops.append(loop)
                remap_times.append(remap_time if remap_time is not None else 0)
                transform_times.append(transform_time if transform_time is not None else 0)
                durations.append(duration)

        i += 1

    return loops, remap_times, transform_times, durations

def plot_data(loops, remap_times, transform_times, durations):
    plt.figure(figsize=(12, 6))
    
    plt.plot(loops, remap_times, marker='o', linestyle='-', label='Remap Time (ms)')
    plt.plot(loops, transform_times, marker='s', linestyle='-', label='Transform Color Time (ms)')
    plt.plot(loops, durations, marker='^', linestyle='-', label='Loop Duration (ms)')
    
    plt.xlabel('Loop Index')
    plt.ylabel('Time (ms)')
    plt.title('Log File Timing Analysis')
    plt.legend()
    plt.grid(True)
    
    plt.show()

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
    
    #loops, remap_times, transform_times, durations = parse_log_file(log_content)
    #plot_data(loops, remap_times, transform_times, durations)