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
    
    commandText = f"\n{menupath}\n\navailable commands:\n{commandList}\n\n"

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

# Prints a dictionary in nicer format
def tabulate_dict(data, headers = [], filter = None, tablefmt = 'rounded_grid'):
    # Tabuelate wants an array to make a nice looking table
    array = []
    for key in data:
        # filter = None means no filter, add all values to array
        if filter == None or key in filter:
            array.append([key, str(data[key])])
    return tabulate(array, headers, tablefmt=tablefmt)

def print_dict(data, filter = None):
    return tabulate_dict(data, filter = filter, tablefmt = 'plain')