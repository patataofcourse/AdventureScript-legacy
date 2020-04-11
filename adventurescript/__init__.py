from adventurescript import commands, exceptions
import os
import platform

add_parameters = {}
status = ""

class ContextInfo:
    def __init__(self, script, show, wait, query, pointer=1, flags={}):
        self.script = script
        self.show = show
        self.wait = wait
        self.ask = query
        self.pointer = pointer
        self.flags = flags
    def ending(self, end):
        global status
        status = f"ending {end}"
    def save(self): #TODO
        pass
    def reload(self): #TODO
        pass
    def query(self, text, choices):
        return self.ask(self, text, choices)

def pause():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def askinput(info, text, choices):
    if text != "":
        info.show(text)
    c = 1
    for ch in choices:
        info.show(f"{c}. {ch}")
        c += 1
    result = ""
    while result == ""  and result not in (strrange(len(choices)) + ["r", "s"]):
        result = input(">")
    return result

def strrange(max): # Wonder if this is actually necessary
    r = list(range(1, max+1))
    sr = []
    for num in r:
        sr.append(str(num))
    return sr

def check_commands(info, line):
    if line.startswith("[") and line.endswith("]"):
        line = line[1:-1].split(";")
        line = [line[0].split(" ")[0], " ".join(line[0].split(" ")[1:])] + line[1:]
        for command in commands.commands:
            if command.__name__ == line[0]:
                kwargs = {}
                for pair in line[1:]:
                    pair = pair.split("=")
                    kwargs[pair[0].strip()] = pair[1].strip().strip("\"") #TODO: Remove that last strip whenever I add variables, and add variable checking or some shit
                command(info, **kwargs)
                return True
        return False
    elif line.endswith("[n]"):
        line = line[:-3]
        info.show(line)
        commands.n(info)
        return True
    else:
        return False

def parse(filename, show = print, wait_for_input = pause, query=askinput):
    info = ContextInfo(open(filename + ".adv").read().split("\n"), show, wait_for_input, query)
    while info.pointer <= len(info.script):
        print(info.pointer)
        line = info.script[info.pointer-1].rstrip()
        if not line.startswith("#"):
            result = check_commands(info, line)
            if not result:
                show(line)
        info.pointer += 1
        if status.startswith("ending"):
            return " ".join(status.split(" ")[1:])
    raise exceptions.ScriptEndException()

# async def asyncparse() --- should finish standard parse first