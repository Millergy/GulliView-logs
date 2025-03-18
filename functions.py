#%% Standard modules
from tabulate import tabulate

#%% Command handler
def run_command(commands, menupath = "path: start", printFunction = None):
    
    print("\n-----new command-----\n")
    
    if type(commands) == type(list()):
        commands[0]()
        commands = commands[1]
    
    keys = list(commands.keys())
    
    #Format available commands
    commandList = f"\t{keys[0]}"
    for i in range(1,len(keys)):
        commandList = commandList + "\n\t" + keys[i]
    
    commandText = f"\n{menupath}\npress enter to return/close\n\navailable commands:\n{commandList}\n\n"

    while True:
        
        userInput = input(commandText)
        
        print("\n")
        
        #Is input valid?
        exitInput = userInput == ""
        regularInput = userInput in keys
        capitalInput = userInput.capitalize() in keys
        if not (regularInput or capitalInput or exitInput):
            print("\n-----unvalid command, try again-----\n")
            continue
        
        #If empty, break
        if userInput == "":
            return True
        
        #If dict, it is a submenu
        if type(commands[userInput]) == type(dict()):
            run_command(commands[userInput], menupath + "/" + userInput)
        
        #If array, it is a submenu with a function before
        elif type(commands[userInput]) == type(list()):
            commands[userInput][0]()
            run_command(commands[userInput][1], menupath + "/" + userInput, 
                       commands[userInput][0])
        
        #Else it is a function
        else:
            commands[userInput]()
            
        print("\n-----back-----\n")
        
        if printFunction:
            printFunction()

# Press enter to continue
def user_acknowledge(msg):
    print(msg)
    print("Press any button to continue...")
    input()  # Waits for user input before proceeding

# Handles input of integer from 0 to "high"
def input_number(high, prompt):
    while True:
        userInput = input(prompt)
        if userInput == "":
            return None
        try:
            number = int(userInput)
        except:
            print("-----invalid number-----")
            continue
        
        if number > high or number <= 0:
            print("-----number not in range-----")
            continue
        
        break
    return number

# Returns dict as a string looking like a table
def tabulate_dict(data, headers = [], tablefmt = 'rounded_grid'):
    array = []
    for key in data:
        array.append([key, data[key]])
    return tabulate(array, headers, tablefmt=tablefmt)

def try_int_float_convert(value):
    try:
        if "." in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        return value