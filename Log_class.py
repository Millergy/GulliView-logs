#%% Standard modules
from tqdm import tqdm
import os
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

#%% Custom modules
from functions import try_int_float_convert
from functions import tabulate_dict

class Log:

    def __init__(self, filepath, general_log_filename, show_progress = True):
        # Init dicts for data import
        self.data = {}      # Log data
        self.other = {}     # Data not useful at this time
        self.time_data = {} # Time stats
        
        # Go through all files in folder
        if show_progress:
            for log_filename in tqdm(os.listdir(filepath), desc="Importing data"):
                self.import_file(filepath, log_filename)
        else:
            for log_filename in os.listdir(filepath):
                self.import_file(filepath, log_filename)

        # For testing
        # self.import_file(filepath, general_log_filename)
        # self.import_file(filepath, "camera_0_output-fast.log", 150)

        
        # Put general data in seperate dict
        self.general_data = self.data[general_log_filename]
        del self.data[general_log_filename]
        self.format_general()

        if show_progress:
            for i in tqdm(self.data, desc="Formatting data"):
                self.format_data(i)
        else:
            for i in self.data:
                self.format_data(i)

    # name of folder with archived logs, it is the timestamp of the log
    def return_folder_name(self):
        return str(self.general_data["TIME"]).replace(":",";")
    
    # general log attributes
    def return_attributes(self):
        return self.general_data
    
    # keys for time data
    def return_keys(self):
        filename = list(self.time_data.keys())[0]
        return list(self.time_data[filename].keys())

    # Convert text in files to dict
    def import_file(self, folder_filepath, filename, limit = None):
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
    def format_data(self, key):
        data_dict = self.data[key].copy()
        time_dict = {}

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
            elif len(first_split_space) == 2 and first_split_space[1] == "ms":
                time_dict[category] = self.convert_units_to_float(array)
            
            # key: xxx us
            elif len(first_split_space) == 2 and first_split_space[1] == "us":
                time_dict[category] = self.convert_units_to_float(array, 1000)
            
            # key: value=xxx ms
            elif len(first_split_equal) >= 2 and first_split_equal_space[1] == "ms":
                time_dict[category] = self.convert_units_to_float(array)
            
            # key: value=xxx us
            elif len(first_split_equal) >= 2 and first_split_equal_space[1] == "us":
                time_dict[category] = self.convert_units_to_float(array, 1000)

            # else:
            #     print(category, data_dict[category])
            
            self.time_data[key] = time_dict

    def box_plot_all(self):
        

        # Create a 2x2 grid for plotting
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Flatten axes array for easy iteration
        axes = axes.flatten()

        # Iterate over the dictionary and plot
        for ax, (title, plot_data) in zip(axes, self.time_data.items()):
            sns.boxplot(data=list(plot_data.values()), ax=ax)
            ax.set_xticklabels(plot_data.keys())  # Set labels for x-axis
            ax.set_title(title)  # Set plot title
            # ax.set_ylim(0,100)  # Set custom y-axis limits

        # Adjust layout
        plt.tight_layout()
        plt.show()


# Testing class object creation
if __name__ == "__main__":
    new_log = Log("manual_copy_logs", "general.log")
    from functions import tabulate_dict
    # print(tabulate_dict(new_log.return_attributes(), ["Type", "Value"]))