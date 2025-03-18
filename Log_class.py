#%% Standard modules
from tqdm import tqdm
import os
import datetime as dt

class Log:

    def __init__(self, filepath, general_log_filename):
        self.data, self.general_data, self.other = self.text_to_dict(filepath, general_log_filename)
        

        self.format_general()

    # name of folder with archived logs, it is the timestamp of the log
    def return_folder_name(self):
        return str(self.general_data["TIME"]).replace(":",";")
    
    def return_attributes(self):
        return self.general_data

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

    def format_general(self):
        for key in self.general_data:

            # If 0/1 change to True/False, else convert to int or float
            if self.general_data[key] == "0":
                self.general_data[key] = False
            elif self.general_data[key] == "1":
                self.general_data[key] = True
            else:
                try:
                    if "." in self.general_data[key]:
                        print(self.general_data[key])
                        self.general_data[key] = float(self.general_data[key])
                    else:
                        self.general_data[key] = int(self.general_data[key])
                except ValueError:
                    pass
            
            
        
        # Change TIME to datetime object
        self.general_data["TIME"] = dt.datetime.strptime(self.general_data["TIME"], "%Y-%m-%d %H:%M:%S")

# Testing class object creation
if __name__ == "__main__":
    new_log = Log("manual_copy_logs", "general.log")
    from functions import tabulate_dict
    print(tabulate_dict(new_log.return_attributes(), ["Type", "Value"]))