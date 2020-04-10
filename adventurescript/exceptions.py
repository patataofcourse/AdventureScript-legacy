class ScriptEndException(Exception):
    def __init__(self):
        self.args = ("Reached end of script!",)