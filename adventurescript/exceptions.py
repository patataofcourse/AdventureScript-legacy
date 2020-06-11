class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)

class CommandException(Exception):
    def __init__(self, scriptname, line, cmdname, info=""):
        self.args = (f"Error in script '{scriptname}'.adv, line {line}, in command {cmdname}: {info}",)

class UndefinedVariableError(CommandException):
    def __init__(self, scriptname, line, cmdname, varname):
        self.args = (f"Variable {varname} doesn't exist! ({scriptname}.adv, line {line}, command {cmdname})",)