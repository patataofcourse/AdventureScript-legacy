import asyncio
from adventurescript import commands, exceptions
import os
import platform

add_parameters = {}

class ContextInfo:
    def __init__(self, name, save_id, show, wait, query, is_async, pass_info, pointer=1, flags={}, variables={}, lists={}):
        self.gamename = name
        self.scriptname = f"script/{name}/start"
        self.script = open(self.scriptname + ".asf").read().split("\n")
        self.save_id = save_id
        self.showfunc = show
        self.waitfunc = wait
        self.queryfunc = query
        self.pointer = pointer
        self.flags = flags
        self.variables = variables
        self.lists = lists
        self.is_async = is_async
        self.pass_info = pass_info
        self.status = "ok"
        self.allow_save = True
    def ending(self, end):
        self.status = f"ending {end}"
    def save(self, sq=False):
        svfile = open(f"save/{self.gamename}/{self.save_id}.asv","w")
        svfile.write("}{".join((self.scriptname,str(self.pointer)))+"}"+str(self.flags)+str(self.variables)+str(self.lists)[:-1])
        svfile.close()
        if sq:
            self.status = "quit"
    def reload(self):
        save = open(f"save/{self.gamename}/{self.save_id}.asv").read().split("}{")
        self.scriptname = save[0]
        self.script = open(f"{self.scriptname}.asf").read().split("\n")
        self.pointer = int(save[1])
        self.flags = eval("{"+save[2]+"}")
        self.variables = eval("{"+save[3]+"}")
        self.flags = eval("{"+save[4]+"}")
    async def show(self, text):
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

def pause():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def askinput(info, text, choices, allow_save):
    if text != "":
        info.showfunc(text)
    c = 1
    for ch in choices:
        info.showfunc(f"{c}. {ch}")
        c += 1
    result = ""
    while result not in (strrange(len(choices))):
        result = input(">")
        if allow_save:
            if result == "s":
                info.save()
                info.showfunc("Saved!")
            elif result == "r":
                try:
                    open(f"save/{info.gamename}/{info.save_id}.asv").read().split("}{")
                except:
                    info.showfunc("No save exists!")
                else:
                    info.showfunc("Save restored!")
                    info.reload()
                    return 0
    return result

def strrange(max):
    r = list(range(1, max+1))
    sr = []
    for num in r:
        sr.append(str(num))
    return sr

def formatcmd(text):
    pass
'''
This command requires:
-checking for "" and ''
-checking for +, -, * and /
'''

async def check_commands(info, line):
    if line == "":
        return False
    elif line.startswith("[") and line.endswith("]"):
        line = line[1:-1].split(";")
        line = [line[0].split(" ")[0], " ".join(line[0].split(" ")[1:])] + line[1:]
        for command in commands.commands:
            if command.__name__ == line[0]:
                kwargs = {}
                if line[1] == "":
                    await command(info)
                    return True
                for pair in line[1:]:
                    pair = pair.split("=")
                    kwargs[pair[0].strip()] = pair[1].strip().strip("\"") #TODO: Make the thing interpret properly
                await command(info, **kwargs)
                return True
        return False
    elif line.endswith("[n]"):
        line = line[:-3]
        await info.show(line)
        await commands.n(info)
        return True
    else:
        return False

async def parse(name, save_id=0, show = print, wait = pause, query=askinput, pass_info = False, addons = [], is_async=False):
    info = ContextInfo(name, save_id, show, wait, query, is_async, pass_info)
    for addon in addons:
        try:
            addon.setup(info)
            commands.commands += addon.commands
        except Exception as e:
            print (f"Exception while attempting to add addon {addon.__name__}:", e)
    try:
        save = open(f"save/{info.gamename}/{info.save_id}.asv").read().split("}{")
        await info.show("A save file has been detected. Would you like to restore it?")
        response = await info.query("",("Yes", "No"), False)
        if response == 2:
            await info.show("Starting a new game...")
        else:
            await info.reload()
            await info.show("Save restored!")
        await info.wait()
    except:
        pass
    while info.pointer <= len(info.script):
        line = info.script[info.pointer-1].rstrip()
        if not line.startswith("#"):
            result = await check_commands(info, line)
            if not result:
                await info.show(line)
        info.pointer += 1
        if info.status == "ok":
            pass
        elif info.status.startswith("ending") or info.status == "quit":
            return info.status
        else:
            raise Exception("Unknown status!")

    raise exceptions.ScriptEndException()

def parse_sync(name, save_id=0, show = print, wait = pause, query = askinput, pass_info = False, addons = []):
    return asyncio.run(parse(name, save_id, show, wait, query, pass_info, addons))