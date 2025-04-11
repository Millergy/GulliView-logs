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
        
        # If in optimized mode, run prod code
        if not __debug__:
            self.init_old(filepath, general_log_filename, show_progress)
            return

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
        self.other = {}     # Data not useful at this time

        # Format data
        if show_progress:
            for i in tqdm(self.data.keys(), desc="Formatting data"):
                self.data[i] = self.format_data(data[i])
        else:
            for i in self.data.keys():
                self.data[i] = self.format_data(data[i])

    def init_old(self, filepath, general_log_filename, show_progress = True):
        # Init dicts for data import
        self.data = {}      # Log data
        self.other = {}     # Data not useful at this time
        self.time_data = {} # Time stats
        
        # Go through all files in folder
        if show_progress:
            for log_filename in tqdm(os.listdir(filepath), desc="Importing data"):
                self.import_file_old(filepath, log_filename)
        else:
            for log_filename in os.listdir(filepath):
                self.import_file_old(filepath, log_filename)
        
        # Put general data in seperate dict
        self.general_data = self.data[general_log_filename]
        del self.data[general_log_filename]
        self.format_general()

        if show_progress:
            for i in tqdm(self.data, desc="Formatting data"):
                self.format_data_old(i)
        else:
            for i in self.data:
                self.format_data_old(i)

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
    
    def import_file_old(self, folder_filepath, filename, limit = None):
        # If log data does not follow expected fomrat it is put in "other"
        # Used for debugging
        self.other[filename] = []

        filepath = os.path.join(folder_filepath, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            for i,line in enumerate(file):
                
                # Get limit first lines of file for debugging
                if limit and i >= limit:
                    return

                # ':' represents data, otherwise it is just info and is put in 'other'
                if ':' in line:
                    # Group data by key, the key is the string before the first ':'
                    # For every key there is a list with the values
                    key, value = line.strip().split(":", 1)
                    self.data.setdefault(filename, {}).setdefault(key, []).append(value.strip())

                elif not line in self.other[filename]:
                    self.other[filename].append(line)

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
    def format_data_old(self, key):
        data_dict = self.data[key].copy()
        value_dict = {}

        for category in data_dict:
            array = data_dict[category]

            # Assume all values follow same format
            first_split_space = array[0].split(" ")
            first_split_equal = array[0].split("=")
            first_split_equal_space = first_split_equal[-1].split(" ")

            # If value is alone we just flatten list, possibly not needed 
            if len(array) == 1:
                data_dict[category] = array[0]

            # Value cannot be split
            elif len(first_split_space) == 1:
                new_array = []
                for i in array:
                    new_array.append(try_int_float_convert(i))
                data_dict[category] = new_array

            # key: xxx ms
            elif len(first_split_space) == 2 and len(first_split_space) >=2 and first_split_space[1] == "ms":
                value_dict[category + " (ms)"] = self.convert_units_to_float(array)
            
            # key: xxx us
            elif len(first_split_space) == 2 and len(first_split_space) >=2 and first_split_space[1] == "us":
                value_dict[category + " (us)"] = self.convert_units_to_float(array)
            
            # key: xxx ns
            elif len(first_split_space) == 2 and len(first_split_space) >=2 and first_split_space[1] == "ns":
                value_dict[category + " (ns)"] = self.convert_units_to_float(array)
            
            # key: xxx Hz
            elif len(first_split_space) == 2 and len(first_split_space) >=2 and first_split_space[1] == "Hz":
                value_dict[category + " (Hz)"] = self.convert_units_to_float(array)
            
            # key: value=xxx ms
            elif len(first_split_equal) >= 2 and len(first_split_equal_space) >= 2 and first_split_equal_space[1] == "ms":
                value_dict[category + " (ms)"] = self.convert_units_to_float(array)
            
            # key: value=xxx us
            elif len(first_split_equal) >= 2 and len(first_split_equal_space) >= 2 and first_split_equal_space[1] == "us":
                value_dict[category + " (us)"] = self.convert_units_to_float(array)
            
            # key: value=xxx ns
            elif len(first_split_equal) >= 2 and len(first_split_equal_space) >= 2 and first_split_equal_space[1] == "ns":
                value_dict[category + " (ns)"] = self.convert_units_to_float(array)
            
            # key: value=xxx Hz
            elif len(first_split_equal) >= 2 and len(first_split_equal_space) >= 2 and first_split_equal_space[1] == "Hz":
                value_dict[category + " (Hz)"] = self.convert_units_to_float(array)

            # else:
            #     print(category, data_dict[category])
            
            self.time_data[key] = value_dict

    # formats data into dicts for plotting
    def format_data(self, data): # data is values from one file as a dict
        formatted_data = {}

        for i,key in enumerate(data):
            sub_data = data[i]  # List of all elements

            split_array = list(map(lambda item: item.split(","), sub_data))
            print(split_array)


        return formatted_data