class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)

class CommandException(Exception):
    def __init__(self, scriptname, line, cmdname):
        self.args = (f"Error in script '{scriptname}'.adv, line {line}, in command {cmdname}",)

class NonBoolFlagError(CommandException):
    def __init__(self, scriptname, line, cmdname, flagname):
        self.args = (f"Flag {flagname} not defined to a boolean value ({scriptname}.adv, line {line}, command {cmdname}",)