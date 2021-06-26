from adventurescript import commands, exceptions, parsecmd
from adventurescript.inventory import Inventory

class ContextInfo:
    def __init__(self, gamename, save_id, show, wait, query, is_async, pass_info, load_file):
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
        self.pass_info = pass_info
        self.flags = {}
        self.variables = {}
        self.lists = {}
        self.extrainvs = {} #Added for shop storage purposes and crap
        self.achievements = []
        for a in self.load_save(True).split(" "):
            if a == "":
                continue
            if not a.isdigit():
                raise exceptions.InvalidAchievementData(self.save_id)
            name = None
            for ach in self.gameinfo["achievements"]:
                if self.gameinfo["achievements"][ach]["num"] == int(a):
                    name = ach
                    break
            if name == None:
                raise Exception(f"invalid achievement {a}")
            self.achievements.append(name)
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
        svfile = self.load_save(mode="w")
        if hasattr(self, "inventory"):
            invtext = "{"+str(self.inventory)+"}"
        else:
            invtext = ""
        svfile.write("}{".join((self.scriptname,str(self.pointer),str(self.allow_save)))+"}"+str(self.flags)+str(self.variables)+str(self.lists)+invtext+str(self.extrainvs)[:-1])
        for slot in self.extra_slots:
            svfile.write("}{"+repr(self.extra_slots[slot]))
        svfile.close()
        if sq:
            self.status = "quit sv"
    def quit(self):
        '''Quits the game'''
        self.status = "quit"
    def reload(self):
        '''Brings the game back to its state before the last save'''
        save = self.load_save().split("}{")
        self.scriptname = save[0]
        self.script = self.load_script(self.scriptname).split("\n")
        self.pointer = int(save[1]) -1
        self.allow_save = bool(save[2])
        self.flags = eval("{"+save[3]+"}")
        self.variables = eval("{"+save[4]+"}")
        self.lists = eval("{"+save[5]+"}")
        self.inventory.recreate(*eval(save[6]))
        c = 7
        for slot in self.extra_slots:
            self.extra_slots[slot] = eval(save[c])
            c+=1
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
                    var = self.lists[word.split(".")[0][2:]]
                else:
                    var = self.variables[word.split(".")[0][1:]]
                if len(word.split(".")) > 1:
                    op = word.split(".")[1:]
                    word = await parsecmd.manage_operations(var, op, False)
                    word = str(word) if type(word) != str else word
                else:
                    word = str(var)
            if word.startswith("&"):
                if word.startswith("&&"):
                    inv = self.inventory
                else:
                    inv = self.extrainvs[word.split(".")[0][1:]]
                if len(word.split(".")) > 1:
                    op = word.split(".")[1:]
                    word = str(await parsecmd.manage_operations(inv, op, False))
                else:
                    word = repr(inv)
            text2.append(word)
        text = " ".join(text2)

        if self.pass_info:
            f = self.showfunc(self, text, **kwargs)
        else:
            f = self.showfunc(text, **kwargs)
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
        if self.pass_info:
            f = self.waitfunc(self)
        else:
            f = self.waitfunc()
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