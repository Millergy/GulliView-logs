#%% Custom modules
from Data_class import Data

#%% Command handler
def runCommand(commands, filepath = "path: start", printFunction = None):
    
    print("\n-----new command-----\n")
    
    if type(commands) == type(list()):
        commands[0]()
        commands = commands[1]
    
    keys = list(commands.keys())
    
    #Format available commands
    commandList = f"\t{keys[0]}"
    for i in range(1,len(keys)):
        commandList = commandList + "\n\t" + keys[i]
    
    commandText = f"\n{filepath}\n\nAvailable commands:\n{commandList}\n\n"
    while True:
        
        userInput = input(commandText)
        
        print("\n")
        
        #Is input valid?
        exitInput = userInput == ""
        regularInput = userInput in keys
        capitalInput = userInput.capitalize() in keys
        if not (regularInput or capitalInput or exitInput):
            print("\n-----Unvalid command, try again-----\n")
            continue
        
        #If empty, break
        if userInput == "":
            return True
        
        #If dict, it is a submenu
        if type(commands[userInput]) == type(dict()):
            runCommand(commands[userInput], filepath + "/" + userInput)
        
        #If array, it is a submenu with a function before
        elif type(commands[userInput]) == type(list()):
            commands[userInput][0]()
            runCommand(commands[userInput][1], filepath + "/" + userInput, 
                       commands[userInput][0])
        
        #Else it is a function
        else:
            commands[userInput]()
            
        print("\n-----Back-----\n")
        
        if printFunction:
            printFunction()

data = Data()
while True:
    if runCommand(data.returnCommands()):
        break