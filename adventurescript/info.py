from adventurescript import exceptions, parsecmd

class ContextInfo:
    def __init__(self, name, save_id, show, wait, query, is_async, pass_info):
        self.gamename = name
        self.gameinfo = eval("{"+",".join(open(f"games/{name}/info").read().split("\n"))+"}")
        print(self.gameinfo)
        self.scriptname = f"games/{name}/script/start"
        self.script = open(self.scriptname + ".asf").read().split("\n")
        self.save_id = save_id
        self.showfunc = show
        self.waitfunc = wait
        self.queryfunc = query
        self.is_async = is_async
        self.pass_info = pass_info
        self.flags = {}
        self.variables = {}
        self.lists = {}
        self.pointer = 1
        self.status = "ok"
        self.allow_save = True
        self.extra_slots = []
        self.forbidden_characters = ["%", "$", ".", "[", "]", "{", "}", "=", ";", "\\", "(", ")", " ", "\n", "\"", "'", ","]
    def ending(self, end):
        self.status = f"ending {end}"
    def save(self, sq=False):
        svfile = open(f"games/{self.gamename}/save/{self.save_id}.asv","w")
        svfile.write("}{".join((self.scriptname,str(self.pointer)))+"}"+str(self.flags)+str(self.variables)+str(self.lists)[:-1])
        for slot in self.extra_slots:
            data = getattr(self, slot)
            svfile.write("}{"+str(data))
        svfile.close()
        if sq:
            self.status = "quit sv"
    def quit(self):
        self.status = "quit"
    def reload(self):
        save = open(f"games/{self.gamename}/save/{self.save_id}.asv").read().split("}{")
        self.scriptname = save[0]
        self.script = open(f"{self.scriptname}.asf").read().split("\n")
        self.pointer = int(save[1]) -1
        self.flags = eval("{"+save[2]+"}")
        self.variables = eval("{"+save[3]+"}")
        self.lists = eval("{"+save[4]+"}")
        c = 5
        for slot in self.extra_slots:
            exec('self.' + slot + '= save[c]')
            c+=1
    async def show(self, text):
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
                    word = str(parsecmd.manage_operations(var, op))
                else:
                    word = str(var)
            text2.append(word)
        text = " ".join(text2)

        if self.pass_info:
            f = self.showfunc(self, text)
        else:
            f = self.showfunc(text)
        if self.is_async:
            return await f
        else:
            return f
    async def wait(self):
        if self.pass_info:
            f = self.waitfunc(self)
        else:
            f = self.waitfunc()
        if self.is_async:
            return await f
        else:
            return f
    async def query(self, text, choices, allow_save=None):
        if allow_save == None:
            allow_save = self.allow_save
        f = self.queryfunc(self, text, choices, allow_save)
        if self.is_async:
            return await f
        else:
            return f
