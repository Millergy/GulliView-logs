#%% Standard modules
from tqdm import tqdm
import os

class Log:

    def __init__(self, filepath, general_log_filename):

        self.data, general_data, self.other = self.text_to_dict(filepath, general_log_filename)

        # Get timestamp of log as string, happens to be a single element list for now
        self.timestamp_string = self.data[self.general_log_filename]["Time"]

    # name of folder with archived logs
    def return_folder_name(self):
        return self.timestamp_string.replace(":",";")
    
    def return_attributes(self):
        return self.data[self.general_log_filename]

    # Convert text in files to dict
    def text_to_dict(self, filepath, general_log_filename):

        # Init dict
        data = {}
        general_data = {}
        other = {}

        # Go through all files in folder
        for log_filename in tqdm(os.listdir(filepath), desc="Importing data"):
            log_filepath = os.path.join(filepath, log_filename)

            # Init dict for logs, 'other' is for general log outputs, used to debug functionality
            data[log_filename] = {}
            other[log_filename] = []

            with open(log_filepath, "r", encoding="utf-8") as file:
                for line in file:

                    # general_log values not put in arrays
                    if log_filename == general_log_filename:
                        key, value = line.strip().split(":", 1)
                        general_data[key] = value.strip()

                    # ':' represents data, otherwise it is just info and is put in 'other'
                    elif ':' in line:

                        # Group data by key, the key is the string before the first ':'
                        # For every key there is a list with the values
                        key, value = line.strip().split(":", 1)
                        data[log_filename].setdefault(key, []).append(value.strip())

                    elif not line in other[log_filename]:
                        other[log_filename].append(line)

        return data, general_data, other


    