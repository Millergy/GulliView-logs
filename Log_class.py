#%% Standard modules
from tqdm import tqdm
import os
import datetime as dt

class Log:

    def __init__(self, filepath, general_log_filename):
        self.data, self.general_data, self.other = self.text_to_dict(filepath, general_log_filename)
        
        self.format_general()

        # For testing
        self.format_data(self.data["camera_0_output-fast.log"])

        # for i in self.data:
        #     self.format_data(self.data[i])

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

            # If log data does not follow expected fomrat it is put in "other"
            # Used for debugging
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
                        data.setdefault(log_filename, {}).setdefault(key, []).append(value.strip())

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
                        self.general_data[key] = float(self.general_data[key])
                    else:
                        self.general_data[key] = int(self.general_data[key])
                except ValueError:
                    pass

        # Change TIME to datetime object
        self.general_data["TIME"] = dt.datetime.strptime(self.general_data["TIME"], "%Y-%m-%d %H:%M:%S")

    def convert_units_to_float(self, array, unit = "ms"):
        time_list = []
        for value in array:
            sep = value.split(" ")
        
            if len(sep) == 2 and sep[1] == unit:
                try:
                    time = float(sep[0])
                    time_list.append(time)
                except ValueError:
                    print(sep[0], " could not be converted to float")
        return time_list

    def format_data(self, data_dict):
        for category in data_dict:
            array = data_dict[category]
            # print(array,"\n")

            # If value is alone we just flatten list, possibly not needed 
            if len(array) == 1:
                data_dict[category] = array[0]
            else:
                data_dict[category] = self.convert_units_to_float(array)

            print(data_dict[category])


# Testing class object creation
if __name__ == "__main__":
    new_log = Log("manual_copy_logs_short", "general.log")
    from functions import tabulate_dict
    # print(tabulate_dict(new_log.return_attributes(), ["Type", "Value"]))