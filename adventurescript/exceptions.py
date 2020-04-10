class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)

class ArgumentException(Exception):
    def __init__(self, argument, command):
        self.args = ("Error with argument", argument, "in command", command)

class MissingArgumentError(ArgumentException):
    def __init__(self, argument, command):
        self.args = ("Required argument", argument, "missing in command", command)

class MisplacedArgumentError(ArgumentException):
    def __init__(self, argument1, argument2, command):
        self.args = ("Argument", argument2, "placed after argument", argument1, "in command", command)