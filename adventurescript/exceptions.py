#Generic exceptions

class CommandException(Exception):
    def __init__(self, scriptname, line, exception):
        self.args = (f"Error in script {scriptname}, line {line}.: {type(exception).__name__}",)

class ArgumentSyntaxError(Exception):
    def __init__(self, scriptname, line, exception):
        self.args = (f"Error with the arguments. ({scriptname}, line {line}): {type(exception).__name__}",)

class UnwantedArgumentError(CommandException):
    def __init__ (self, scriptname, line, cmdname, argname):
        self.args = (f"Command '{cmdname}' doesn't accept the argument '{argname}'. ({scriptname}, line {line})",)

class MissingArgumentError(CommandException):
    def __init__ (self, scriptname, line, cmdname, argname):
        self.args = (f"Command '{cmdname}' needs the argument'{argname}'. ({scriptname}, line {line})",)

#Undefined variables

class UndefinedObjectError(CommandException):
    def __init__(self, scriptname, line, name):
        self.args = (f"'{varname}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedVariableError(UndefinedObjectError):
    def __init__(self, scriptname, line, varname):
        self.args = (f"Variable '{varname}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedLabelError(UndefinedObjectError):
    def __init__(self, scriptname, line, lblname):
        self.args = (f"Label '{chr(123)+lblname+chr(125)}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedFlagError(UndefinedObjectError):
    def __init__(self, scriptname, line, flagname):
        self.args = (f"Flag '{flagname}' doesn't exist! ({scriptname}, line {line})",)
    
class UndefinedListError(UndefinedObjectError):
    def __init__(self, scriptname, line, listname):
        self.args = (f"List '{listname}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedInventoryError(UndefinedObjectError):
    def __init__(self, scriptname, line, invname):
        self.args = (f"Inventory '{invname}' doesn't exist! ({scriptname}, line {line})",)

class NoDefaultInventoryError(UndefinedInventoryError):
    def __init__(self, scriptname, line):
        self.args = (f"The default inventory isn't set up! ({scriptname}, line {line})",)

#Invalid save/save_p data

class InvalidSaveData(CommandException):
    def __init__(self, id):
        if id != None:
            self.args = (f"Tried to load invalid save data! (save ID {id})",)
        else:
            self.args = (f"Tried to load invalid save data!",)

class InvalidSaveVersion(InvalidSaveData):
    def __init__(self, id, ver):
        if id != None:
            self.args = (f"Save contains invalid AS version {ver}! (save ID {id})",)
        else:
            self.args = (f"Save contains invalid AS version {ver}!",)

class InvalidPersSaveData(CommandException):
    def __init__(self, id):
        if id != None:
            self.args = (f"Tried to load invalid persistent save data! (save ID {id})",)
        else:
            self.args = (f"Tried to load invalid persistent save data!",)

class InvalidAchievementData(InvalidPersSaveData):
    def __init__(self, id):
        if id != None:
            self.args = (f"Tried to load invalid achievement data! (save ID {id})",)
        else:
            self.args = (f"Tried to load invalid achievement data!",)

#Other

class InvalidNameCharacter(CommandException):
    def __init__(self, scriptname, line, vartype, character):
        self.args = (f"{str.title(vartype)} names can't have the character '{character}'! ({scriptname}, line {line})",)

class InvalidOperation(CommandException):
    def __init__(self, scriptname, line, opname):
        self.args = (f"Operation {opname} does not exist! ({scriptname}, line {line})",)

class InvalidStatus(CommandException):
    def __init__(self, scriptname, line, status):
        self.args = (f"Unknown status {status}! ({scriptname}, line {line})",)

class ChoiceArgumentError(CommandException):
    def __init__(self, scriptname, line):
        self.args = (f"The ch/go arguments in a [choice] command aren't corresponding. ({scriptname}, line {line})",)

class CheckArgumentError(CommandException):
    def __init__(self, scriptname, line):
        self.args = (f"The check/go arguments in a [chaincheck] command aren't corresponding. ({scriptname}, line {line})",)

class SwitchArgumentError(CommandException):
    def __init__(self, scriptname, line):
        self.args = (f"The case/go arguments in a [switch] command aren't corresponding. ({scriptname}, line {line})",)

class ScriptEndException(Exception):
    def __init__(self, scriptname):
        self.args = (f"Reached end of script {scriptname}!",)

class OldSaveException(Exception):
    def __init__(self, ver):
        self.args = (f"Tried to load a save from an old version of AdventureScript (v{ver}), which is no longer compatible.",)
        self.ver = ver

class ZeroInventorySizeError(CommandException):
    def __init__(self, scriptname, line):
        self.args = (f"Inventory size can't be 0! ({scriptname}, line {line})",)

#These are to be used when an info isn't present and later caught through the use of try/except

class InvSize(ZeroInventorySizeError):
    def __init__(self):
        pass

class SaveVer(InvalidSaveVersion):
    def __init__(self, ver):
        self.ver = ver