import asyncio
from adventurescript import commands, exceptions
import os
import platform

add_parameters = {}
status = "ok"

class ContextInfo:
    def __init__(self, scriptname, show, wait, query, is_async, pointer=1, flags={}, variables={}, lists={}):
        self.scriptname = scriptname
        self.script = open(scriptname + ".adv").read().split("\n")
        self.showfunc = show
        self.waitfunc = wait
        self.queryfunc = query
        self.pointer = pointer
        self.flags = flags
        self.variables = variables
        self.lists = lists
        self.is_async = is_async
    def ending(self, end):
        global status
        status = f"ending {end}"
    async def save(self): #TODO
        pass
    async def reload(self): #TODO
        pass
    async def show(self, text):
        if self.is_async:
            return await self.showfunc(text)
        else:
            return self.showfunc(text)
    async def wait(self):
        if self.is_async:
            return await self.waitfunc()
        else:
            return self.waitfunc()
    async def query(self, text, choices):
        if self.is_async:
            return await self.queryfunc(self, text, choices)
        else:
            return self.queryfunc(self, text, choices)

def pause():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def askinput(info, text, choices):
    if text != "":
        info.showfunc(text)
    c = 1
    for ch in choices:
        info.showfunc(f"{c}. {ch}")
        c += 1
    result = ""
    while result not in (strrange(len(choices)) + ["r", "s"]):
        result = input(">")
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

async def parse(filename, show = print, wait_for_input = pause, query=askinput, is_async=False):
    info = ContextInfo(filename, show, wait_for_input, query, is_async)
    while info.pointer <= len(info.script):
        line = info.script[info.pointer-1].rstrip()
        if not line.startswith("#"):
            result = await check_commands(info, line)
            if not result:
                await info.show(line)
        info.pointer += 1
        if status.startswith("ending"):
            return " ".join(status.split(" ")[1:])
    raise exceptions.ScriptEndException()

def parse_sync(filename, show = print, wait_for_input = pause, query = askinput):
    return asyncio.run(parse(filename, show, wait_for_input, query))