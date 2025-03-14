#%% Standard modules
from tqdm import tqdm
import os

class Log:

    def __init__(self, filepath, general_log_filename):

        self.general_log_filename = general_log_filename

        self.data, self.other = self.text_to_dict(filepath)

        # Get timestamp of log as string, happens to be a single element list for now
        self.timestamp_string = self.data[self.general_log_filename]["Time"][0]

    # name of folder with archived logs
    def return_folder_name(self):
        return self.timestamp_string.replace(":",";")

    # Convert text in files to dict
    def text_to_dict(self, filepath):

        # Init dict
        data = {}
        other = {}

        # Go through all files in folder
        for log_filename in tqdm(os.listdir(filepath), desc="Importing data"):
            log_filepath = os.path.join(filepath, log_filename)

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


    