import json

from adventurescript import commands, exceptions, operations, parsecmd, version
from adventurescript.inventory import Inventory

class ContextInfo:
    def __init__(self, gamename, save_id, show, wait, query, is_async, load_file):
        self.loadfunc = load_file
        self.gamename = gamename
        self.gameinfo = eval("{"+",".join(self.load_file("info").split("\n"))+"}")
        if self.gameinfo.get("achievements", False):
            self.gameinfo["achievements"] = {}
            pos = -1
            for a in eval("[["+"],[".join(self.load_file("achievements").split("\n"))+"]]"):
                pos += 1
                
                if len(a) == 0:
                    continue
                elif len(a) == 1:
                    a_type = "flag"
                    a_args = ()
                else:
                    a_type = a[1]
                    a_args = tuple(a[2:])
                
                self.gameinfo["achievements"][a[0]] = {"type": a_type, "num": pos, "args": a_args}
        if self.gameinfo.get("inventory", False):
            self.inventory = Inventory(self.gameinfo["inventory_size"])
        else:
            self.inventory = None
        self.scriptname = "start"
        self.chapter = ""
        self.script = self.load_script(self.scriptname).split("\n")
        self.pointer = 1
        self.commands = commands.__dict__
        self.save_id = save_id
        self.showfunc = show
        self.waitfunc = wait
        self.queryfunc = query
        self.is_async = is_async
        self.flags = {}
        self.variables = {}
        self.lists = {}
        self.extrainvs = {} #Added for shop storage purposes and crap
        self.achievements = json.loads(self.load_save(True)).get("achievements", [])
        self.status = "ok" #TODO: cmon .-.
        self.allow_save = True
        self.extra_slots = {}
        self.forbidden_characters = ["&", "%", "$", ".", "[", "]", "{", "}", "=", ";", "\\", "(", ")", " ", "\n", "\"", "'", ","]
    def ending(self, end):
        '''Displays a "you got the __ ending" (or similar, depending on implementation) message, then quits the game

        Parameters
        ------------

        end - str
            the ending name to be displayed'''
        self.status = f"ending {end}"
    def save(self, sq=False):
        '''Saves the game

        Parameters
        ------------

        sq - bool, optional (defaults to False)
            if True, saves and quits, otherwise saves and continues'''
        save = {
            "version": version.version,
            "chapter": self.chapter,
            "script": self.scriptname,
            "pointer": self.pointer,
            "allow_save": self.allow_save,
            "flags": self.flags,
            "variables": self.variables,
            "lists": self.lists,
            "default_inv": str(self.inventory), 
            "inventories": self.extrainvs,
            "extra": self.extra_slots
        }
        svfile = self.load_save(mode="w")
        svfile.write(json.dumps(save))
        svfile.close()
        if sq:
            self.status = "quit sv"
    def quit(self):
        '''Quits the game'''
        self.status = "quit"
    def reload(self):
        '''Brings the game back to its state before the last save'''
        save = json.loads(self.load_save())
        try:
            if not version.check(save["version"]):
                raise exceptions.OldSaveException(save["version"])
        except exceptions.SaveVer as e:
            raise exceptions.InvalidSaveVersion(self.id, e.ver)
        self.chapter = save["chapter"]
        self.scriptname = save["script"]
        self.script = self.load_script(self.scriptname).split("\n")
        self.pointer = save["pointer"] -1
        self.allow_save = save["allow_save"]
        self.flags = save["flags"]
        self.variables = save["variables"]
        self.lists = save["lists"]
        if save.get("default_inv"):
            self.inventory.recreate(*eval(save["default_inv"]))
        for item in save["inventories"]:
            self.extrainvs[item] = Inventory().recreate(*eval(save["inventories"][item]))
        self.extra_slots = save["extra"]
    def flag(self, name):
        '''Gets a flag from its name

        Parameters
        ------------

        name - str
            the name of the flag to be obtained'''
        try:
            return self.flags[name]
        except KeyError:
            raise exceptions.UndefinedFlagError(self.scriptname, self.pointer+1, name)
    def var(self, name):
        '''Gets a variable from its name

        Parameters
        ------------

        name - str
            the name of the variable to be obtained'''
        try:
            return self.variables[name]
        except KeyError:
            raise exceptions.UndefinedVariableError(self.scriptname, self.pointer+1, name)
    def list(self, name):
        '''Gets a list from its name

        Parameters
        ------------

        name - str
            the name of the list to be obtained'''
        try:
            return self.lists[name]
        except KeyError:
            raise exceptions.UndefinedListError(self.scriptname, self.pointer+1, name)
    def inv(self, name):
        '''Gets an inventory from its name

        Parameters
        ------------

        name - str
            the name of the inventory to be obtained'''
        try:
            return self.extrainvs[name]
        except KeyError:
            raise exceptions.UndefinedInventoryError(self.scriptname, self.pointer+1, name)
    async def show(self, text, **kwargs):
        '''Manages displaying text using the self.show function
        
        Parameters
        ------------

        text - str
            the raw AdventureScript line to process then display
        
        **kwargs - keyword arguments
            those are passed in case the self.query function is custom and requires extra keyword arguments'''
        if text.strip().startswith("{"):
            for ch in self.forbidden_characters:
                if ch in text[1:text.find("}")]:
                    raise exceptions.InvalidNameCharacter(self.scriptname, self.pointer, "label", ch)
            text = text[text.find("}")+1:]
            text = text.lstrip()
            
        text = text.split(" ")
        text2 = []
        for word in text:
            if word.startswith("$"):
                if word.startswith("$$"):
                    var = self.list(word.split(".")[0][2:])
                else:
                    var = self.var(word.split(".")[0][1:])
                if len(word.split(".")) > 1:
                    op = word.split(".")[1:]
                    word = repr(await operations.manage_operations(var, op))
                else:
                    word = str(var)
            if word.startswith("&"):
                if word.startswith("&&"):
                    inv = self.inventory
                else:
                    inv = self.inv(word.split(".")[0][1:])
                if len(word.split(".")) > 1:
                    op = word.split(".")[1:]
                    word = repr(await operations.manage_operations(inv, op))
                else:
                    word = repr(inv)
            text2.append(word)
        text = " ".join(text2)

        f = self.showfunc(self, text, **kwargs)
        if self.is_async:
            return await f
        else:
            return f
    async def wait(self, **kwargs):
        '''Manages waiting until the player inputs ("next textbox") using the self.wait function
        
        Parameters
        ------------

        **kwargs - keyword arguments
            those are passed in case the self.query function is custom and requires extra keyword arguments'''
        f = self.waitfunc(self)
        if self.is_async:
            return await f
        else:
            return f
    async def query(self, text, choices, allow_save=None, **kwargs):
        '''Manages showing the player a choice and taking their input using the self.query function
        
        Parameters
        ------------

        text - str
            text to be shown immediately before the choice
        
        choices - list [str]
            the different choices to be shown to the player
        
        allow_save - bool, optional (defaults to None)
            if True, the choice allows the player to save the game or restore their save

        **kwargs - keyword arguments
            those are passed in case the self.query function is custom and requires extra keyword arguments'''
        if allow_save == None:
            allow_save = self.allow_save
        f = self.queryfunc(self, text, choices, allow_save, **kwargs)
        if self.is_async:
            return await f
        else:
            return f
    def load_file(self, filename, mode="r"):
        '''Loads a file from the game folder

        Parameters
        ------------
        
        filename - str
            the name of the file to be loaded
        
        mode - str, optional (defaults to "r")
            the mode in which to load the file. See help(open) for more information'''
        return self.loadfunc(self.gamename, filename, mode=mode)
    def load_script(self, scriptname):
        '''Loads a script file (from the game/script folder)'s text content
        Will be loaded inside the current chapter, if any

        Parameters
        ------------
        
        scriptname - str
            the name of the script to be loaded'''
        return self.loadfunc(self.gamename, scriptname, type="script", chapter = self.chapter)
    def load_save(self, persistent = False, mode="r"):
        '''Loads the current player's save

        Parameters
        ------------
        
        persistent - bool, optional (defaults to False)
            whether to load the persistent (achievement) save [True] or the regular save [False]
        
        mode - str, optional (defaults to "r")
            the mode in which to load the save. See help(open) for more information'''
        return self.loadfunc(self.gamename, str(self.save_id if self.save_id != None else "save"), type="save_p" if persistent else "save", mode=mode, create=persistent)