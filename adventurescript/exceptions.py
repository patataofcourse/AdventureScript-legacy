class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)

class CommandException(Exception):
    def __init__(self, scriptname, line, cmdname, info=""):
        self.args = (f"Error in script '{scriptname}'.adv, line {line}, in command {cmdname}: {info}",)

class UndefinedObjectError(Exception):
    def __init__(self, scriptname, line, name, cmdname=None):
        self.args = (f"'{varname}' doesn't exist! ({scriptname}.adv, line {line}{(", command" + cmdname) if cmdname != None else ''})",)

class UndefinedVariableError(UndefinedObjectError):
    def __init__(self, scriptname, line, varname, cmdname=None)):
        self.args = (f"Variable '{varname}' doesn't exist! ({scriptname}.adv, line {line}{(", command" + cmdname) if cmdname != None else ''})",)

class UndefinedLabelError(UndefinedObjectError):
    def __init__(self, scriptname, line, lblname, cmdname=None)):
        self.args = (f"Label '{chr(123)+lblname+chr(125)}' doesn't exist! ({scriptname}.adv, line {line}{(", command" + cmdname) if cmdname != None else ''}",)

class UndefinedFlagError(UndefinedObjectError):
    def __init__(self, scriptname, line, flagname, cmdname=None)):
        self.args = (f"Flag '{flagname}' doesn't exist! ({scriptname}.adv, line {line}{(", command" + cmdname) if cmdname != None else ''})",)
    
class UndefinedListError(UndefinedObjectError):
    def __init__(self, scriptname, line, listname, cmdname=None)):
        self.args = (f"List '{listname}' doesn't exist! ({scriptname}.adv, line {line}{(", command" + cmdname) if cmdname != None else ''})",)