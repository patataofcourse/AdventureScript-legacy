#Command exceptions (commands.py, parsecmd.py)

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

class UndefinedObjectError(Exception):
    def __init__(self, scriptname, line, name):
        self.args = (f"'{varname}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedVariableError(UndefinedObjectError):
    def __init__(self, scriptname, line, varname):
        self.args = (f"Variable '{varname}' doesn't exist! ({scriptname}, line {line})",)

class UndefinedLabelError(UndefinedObjectError):
    def __init__(self, scriptname, line, lblname):
        self.args = (f"Label '{chr(123)+lblname+chr(125)}' doesn't exist! ({scriptname}, line {line}",)

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

#Other

class InvalidNameCharacter(CommandException):
    def __init__(self, scriptname, line, vartype, character):
        self.args = (f"{str.title(vartype)} names can't have the character '{character}'! ({scriptname}, line {line})",)

class ChoiceArgumentError(Exception):
    def __init__(self, scriptname, line):
        self.args = (f"The ch/go arguments in a [choice] command aren't corresponding. ({scriptname}, line {line})",)

class CheckArgumentError(Exception):
    def __init__(self, scriptname, line):
        self.args = (f"The check/go arguments in a [chaincheck] command aren't corresponding. ({scriptname}, line {line})",)

class ScriptEndException(Exception):
    def __init__(self, scriptname):
        self.args = (f"Reached end of script {scriptname}!",)