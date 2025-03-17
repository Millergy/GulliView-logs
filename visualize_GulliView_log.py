#%% Standard modules


#%% Custom modules
from Data_class import Data
from functions import run_command

data = Data()
while True:
    if run_command(data.returnCommands()):
        break