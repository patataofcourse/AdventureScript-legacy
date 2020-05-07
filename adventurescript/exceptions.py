class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)

class CommandException(Exception):
    def __init__(self, scriptname, line, cmdname, info=""):
        self.args = (f"Error in script '{scriptname}'.adv, line {line}, in command {cmdname}:",info)

class NonBoolFlagError(CommandException):
    def __init__(self, scriptname, line, cmdname, flagname):
        self.args = (f"Flag {flagname} not defined to a boolean value ({scriptname}.adv, line {line}, command {cmdname}",)

class UndefinedVariableError(CommandException):
    def __init__(self, scriptname, line, cmdname, varname):
        self.args = (f"Variable {varname} doesn't exist! ({scriptname}.adv, line {line}, command {cmdname})",)