#%% Standard modules
import os

#%% Custom modules
from Data_class import Data
from functions import run_command

# Clear terminal
# Windows (cls) or Linux/macOS (clear)
os.system('cls' if os.name == 'nt' else 'clear')

data = Data()

while True:
    if run_command(data.returnCommands()):
        break