class ScriptEndException(Exception):
    def __init__(self, scriptname):
        self.args = (f"Reached end of script {scriptname} !",)

class CommandException(Exception):
    def __init__(self, scriptname, line, cmdname, info=""):
        self.args = (f"Error in script '{scriptname}'.adv, line {line}, in command {cmdname}: {info}",)

class UndefinedObjectError(Exception):
    def __init__(self, scriptname, line, name):
        self.args = (f"'{varname}' doesn't exist! ({scriptname}.adv, line {line})",)

class UndefinedVariableError(UndefinedObjectError):
    def __init__(self, scriptname, line, varname):
        self.args = (f"Variable '{varname}' doesn't exist! ({scriptname}.adv, line {line})",)

class UndefinedLabelError(UndefinedObjectError):
    def __init__(self, scriptname, line, lblname):
        self.args = (f"Label '{chr(123)+lblname+chr(125)}' doesn't exist! ({scriptname}.adv, line {line}",)

class UndefinedFlagError(UndefinedObjectError):
    def __init__(self, scriptname, line, flagname):
        self.args = (f"Flag '{flagname}' doesn't exist! ({scriptname}.adv, line {line})",)
    
class UndefinedListError(UndefinedObjectError):
    def __init__(self, scriptname, line, listname):
        self.args = (f"List '{listname}' doesn't exist! ({scriptname}.adv, line {line})",)

class UndefinedInventoryError(UndefinedObjectError):
    def __init__(self, scriptname, line, invname):
        self.args = (f"Inventory '{invname}' doesn't exist! ({scriptname}.adv, line {line})",)