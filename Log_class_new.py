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
import numpy as np

#%% Custom modules
from functions import try_int_float_convert

class Log:

    def __init__(self, folderpath, general_log_filename, show_progress = True):
        self.general_data = {}  # Data denoting version, timestamp, etc
        self.other = {}         # Data not useful at this time
        self.data = {}          # Useful stats
        self.values = {}        # Numbers that can be used in plotting
        self.agg_data = {}        # Aggregated data for plotting

        # List of filepaths for files
        filenames = os.listdir(folderpath)

        # Import general
        if general_log_filename in filenames:
            filepath = os.path.join(folderpath, general_log_filename)
            self.import_file(filepath, True)
            self.format_general()
            filenames.remove(general_log_filename)

        # Go through all files in folder
        if show_progress:
            for i in tqdm(filenames, "Importing data"):
                filepath = os.path.join(folderpath, i)
                self.import_file(filepath)
                self.format_data(i)
                self.agg_data[i] = self.aggregate(self.values[i])
        else:
            for i in filenames:
                filepath = os.path.join(folderpath, i)
                self.import_file(filepath)
                self.format_data(i)
                self.agg_data[i] = self.aggregate(self.values[i])
        

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
    def import_file(self, filepath, general = False):
        if not general:
            filename = filepath.split("\\")[-1]
            self.other[filename] = []

        with open(filepath, "r", encoding="utf-8") as file:
            for i,line in enumerate(file):

                # If it is general log file we import a little differently
                if general:
                    key, value = line.strip().split(":", 1)
                    self.general_data[key] = value.strip()
                
                # ':' represents data, otherwise it is just info and is put in 'other'
                elif ':' in line:
                    # Group data by key, the key is the string before the first ':'
                    # For every key there is a list with the values
                    key, value = line.strip().split(":", 1)
                    self.data.setdefault(filename, {}).setdefault(key, []).append(value.strip())

                # If log data does not follow expected fomrat it is put in "other"
                # Used for debugging
                elif not line in self.other[filename]:
                    self.other[filename].append(line)

    def format_general(self):
        
        for key in self.general_data:

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
            split = value.split(" ")
            try:
                time = float(split[0])
                time_list.append(time/factor)
            except ValueError:
                # Used to debug formatting, should never be printed in real world use case
                print("Could not convert to float:", split[0], "in", value)

        return time_list

    # formats data into dicts for plotting
    def format_data(self, filename):

        # If data is {"key" : ["aaa=bb, ccc=dd"]} split into {"key, aaa" : "bb", "key, ccc" : "dd"}
        data = self.data[filename]
        keys = list(data.keys())
        for key in keys:
            if "=" in data[key][0]:
                split_lists = list(map(lambda item: item.split(","), data[key]))
                for sublist in split_lists:
                    for item in sublist:
                        subkey, value = item.split("=")
                        subkey = subkey.strip()
                        data.setdefault(key + ", " + subkey, []).append(value)
                del data[key]
        
        # Convert elements to usable values for plotting
        self.values[filename] = {}
        keys = list(data.keys())
        for key in keys:
            value_list = self.data[filename][key]

            # Assume all values follow same format
            first_split_space = value_list[0].split(" ")

            # Value cannot be split so we try to convert to int or float
            if len(first_split_space) == 1:
                for i in value_list:
                    self.values[filename].setdefault(key, []).append(try_int_float_convert(i))

            # Assume the second is a unit
            elif len(first_split_space) == 2:
                unit = first_split_space[1]
                self.values[filename][f"{key} ({unit})"] = self.convert_units_to_float(value_list)
            
            # # For debugging
            # else:
            #     print(key, self.data[filename][key])

    # Aggregate data (calculate percentiles)
    def aggregate(self, data):
        aggregated_values = {}
        for key in data:
            aggregated_values[key] = list(np.percentile(data[key], [0, 25, 50, 75, 100]))
        return aggregated_values