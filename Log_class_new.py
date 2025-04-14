# Copyright © 2025 Emil Nylander

# This file is part of GulliView logs.

# GulliView logs is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, either version 3 
# of the License, or (at your option) any later version.

# GulliView logs is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.

# You should have received a copy of the GNU General Public License 
# along with GulliView logs. If not, see <https://www.gnu.org/licenses/>.

#%% Standard modules
from tqdm import tqdm
import os
import datetime as dt

#%% Custom modules
from functions import try_int_float_convert

class Log:

    def __init__(self, filepath, general_log_filename, show_progress = True):
        self.other = {}     # Data not useful at this time

        # Go through all files in folder
        if show_progress:
            for log_filename in tqdm(os.listdir(filepath), desc="Importing data"):
                data = self.import_file(filepath, log_filename)
        else:
            for log_filename in os.listdir(filepath):
                data = self.import_file(filepath, log_filename)
        
        # Put general data in seperate dict
        self.general_data = data[general_log_filename]
        del data[general_log_filename]
        self.format_general()

        # Init variables for formatting
        self.data = {}      # Only important values

        # Format data
        if show_progress:
            for i in tqdm(self.data.keys(), desc="Formatting data"):
                self.data[i] = self.format_data(data[i])
        else:
            for i in self.data.keys():
                self.data[i] = self.format_data(data[i])

#%% return data
    # name of folder with archived logs, it is the timestamp of the log
    def return_folder_name(self):
        return str(self.general_data["TIME"]).replace(":",";")
    
    # general log attributes
    def return_attributes(self):
        return self.general_data
    
    # keys for time data
    def return_keys(self):
        all_keys = []
        for filename in self.time_data.keys():
            all_keys += list(self.time_data[filename].keys())
        return all_keys

    # version of code as identifier
    def return_identifier(self):
        return self.general_data["VERSION"] + "\n" + str(self.general_data["TIME"])

#%% used for __init__
    # Convert text in files to dict
    def import_file(self, folder_filepath, filename):
        # If log data does not follow expected fomrat it is put in "other"
        # Used for debugging
        self.other[filename] = []
        data = {}

        filepath = os.path.join(folder_filepath, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            for i,line in enumerate(file):

                # ':' represents data, otherwise it is just info and is put in 'other'
                if ':' in line:
                    # Group data by key, the key is the string before the first ':'
                    # For every key there is a list with the values
                    key, value = line.strip().split(":", 1)
                    data.setdefault(filename, {}).setdefault(key, []).append(value.strip())

                elif not line in self.other[filename]:
                    self.other[filename].append(line)
        
        return data

    def format_general(self):
        
        for key in self.general_data:
            
            # The data is in a nested list, this removes this list
            self.general_data[key] = self.general_data[key][0]

            # If 0/1 change to True/False, else convert to int or float
            if self.general_data[key] == "0":
                self.general_data[key] = False
            elif self.general_data[key] == "1":
                self.general_data[key] = True
            else:
                self.general_data[key] = try_int_float_convert(self.general_data[key])

        # Change TIME to datetime object
        self.general_data["TIME"] = dt.datetime.strptime(self.general_data["TIME"], "%Y-%m-%d %H:%M:%S")

    def convert_units_to_float(self, array, factor = 1):
        time_list = []
        for value in array:
            if "=" in value:
                split = value.split("=")
                split = split[-1].split(" ")
            else:
                split = value.split(" ")

            # Assumes 'xxx ms' is the last two values
            try:
                time = float(split[-2])
                time_list.append(time/factor)
            except ValueError:
                # Used to debug formatting, should not be printed
                print("Could not convert to float:", split[-2], "in", value)

        return time_list

    # formats data into dicts for plotting
    def format_data(self, data): # data is values from one file as a dict
        formatted_data = {}

        import time
        sub_data = data[4]

        start_time = time.time()
        split_array = list(map(lambda item: item.split(","), sub_data))
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Execution time lambda: {execution_time:.2f} seconds")
        print(split_array[:4])

        start_time = time.time()
        split_array = []
        for i in sub_data:
            split_array.append(i.split(","))
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Execution time for loop: {execution_time:.2f} seconds")
        print(split_array[:4])

        # for i,key in enumerate(data):
        #     sub_data = data[i]  # List of all elements
            

            


        return formatted_data