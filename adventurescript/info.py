from adventurescript import commands, exceptions, parsecmd
from adventurescript.inventory import Inventory

class ContextInfo:
    '''A class to keep all the information concerning the current game session
    [Documentation is WIP]

    Attributes
    -----------

    [Handled by __init__ parameters]

    gamename
    
    gameinfo

    scriptname

    script

    commands

    save_id

    showfunc

    waitfunc

    queryfunc

    is_async

    pass_info

    [Given a default value in __init__]

    inventory - adventurescript.inventory.Inventory, optional, will only be made if specified so in the game's info file
        the default inventory, accessible in AdventureScript through && instead of &[inventory name]

    flags - dict {str: bool}

    variables - dict {str: str/int/float/etc.}
    
    lists

    extrainvs
    
    pointer

    status
    
    allow_save

    extra_slots - dict {str: ?}
        a list of extra variables from addons, used for these addons' purposes and kept in the save

    forbidden_characters - list [str], treated as constant
        list of characters which can't be used in flag/variable/list/inventory names (TBI: label names)
        
        those characters are: &%$.[]{}=;\\()"', (plus the space and newline characters)
    '''
    def __init__(self, gamename, save_id, show, wait, query, is_async, pass_info):
        self.gamename = gamename
        self.gameinfo = eval("{"+",".join(open(f"games/{gamename}/info").read().split("\n"))+"}")
        if self.gameinfo.get("inventory", False):
            self.inventory = Inventory(self.gameinfo["inventory_size"])
        self.scriptname = f"games/{gamename}/script/start"
        self.script = open(self.scriptname + ".asf").read().split("\n")
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
        self.pointer = 1
        self.status = "ok"
        self.allow_save = True
        self.extra_slots = [] #TODO: turn it into a dict for ease of use
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

        sq - bool, optional (default False)
            if True, saves and quits, otherwise saves and continues'''
        svfile = open(f"games/{self.gamename}/save/{self.save_id}.asv","w")
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
        save = open(f"games/{self.gamename}/save/{self.save_id}.asv").read().split("}{")
        self.scriptname = save[0]
        self.script = open(f"{self.scriptname}.asf").read().split("\n")
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
        text = text.strip()
        if text.startswith("{"):
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
        
        allow_save - bool, optional
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
