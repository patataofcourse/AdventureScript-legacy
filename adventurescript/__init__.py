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
        ask(self, text, choices)

def pause():
    if platform.system() == "Linux" or platform.system() == "Darwin":
        os.system('read -s -n 1')
    elif platform.system() == "Windows":
        os.system("pause >nul")
    else:
        print("Platform not supported")

def err(text): # Replace with an Exception
    print(text)
    quit()

def askinput(info, text, choices):
    info.show(text)
    c = 1
    for ch in choices:
        info.show(f"{c}. {ch}")
    result = ""
    while result == ""  or int(result) not in :
        result = input(">")

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

def askchoice(name1): #TODO
    pass

def parse(filename, show = print, wait_for_input = pause, choicefunc = askchoice):
    info = ContextInfo(open(filename + ".adv").read().split("\n"), show, wait_for_input)
    while info.pointer < len(info.script):
        print(info.pointer)
        line = info.script[info.pointer-1].rstrip()
        if line.startswith("#"):
            info.pointer += 1
            continue
        elif line.startswith("[choice") and line.endswith("]"):
            atrs = line[7:-1].split(";")
            choicenumber = 1.0
            done = []
            choices = []
            gotos = []
            text = ""
            for atr in atrs:
                if int(choicenumber * 10) != int(choicenumber) * 10:
                    if atr[:atr.find("=")].strip() == "go" + str(int(choicenumber)):
                        if not "go" + str(int(choicenumber)) in done:
                            if "ch" + str(int(choicenumber)) in add_parameters:
                                gotos.append(add_parameters["ch" + str(int(choicenumber))])
                                add_parameters.pop("go" + str(int(choicenumber)))
                            else:
                                gotos.append(int(atr[atr.find("=")+1:].strip()))
                            done.append("go" + str(int(choicenumber)))
                            choicenumber += 0.5
                        else:
                            err ("repeated 'go" + str(int(choicenumber)) + "' argument, you suck")
                    else:
                        err("go" + str(int(choicenumber)) + " argument missing right after ch1 argument, you suck")
                elif atr[:atr.find("=")].strip() == "text":
                    if not "text" in done:
                        if "text" in add_parameters:
                            print (">" + add_parameters["text"].strip("\""))
                            add_parameters.pop("text")
                        else:
                            print (">" + atr[atr.find("=")+1:].strip().strip("\""))
                        done.append("text")
                    else:
                        err ("repeated 'text' argument, you suck")
                elif atr[:atr.find("=")].strip() == "ch" + str(int(choicenumber)):
                    if not "ch" + str(int(choicenumber)) in done:
                        if "ch" + str(int(choicenumber)) in add_parameters:
                            choices.append(add_parameters["ch" + str(int(choicenumber))].strip("\""))
                            add_parameters.pop("ch" + str(int(choicenumber)))
                        else:
                            choices.append(atr[atr.find("=")+1:].strip().strip("\""))
                        choicenumber += 0.5
                        done.append("ch" + str(int(choicenumber)))
                    else:
                        err ("repeated ch" + str(int(choicenumber)) + " argument, you suck")
                elif atr[:atr.find("=")].strip() == "flags":
                    print ("//Use of flags attribute not supported yet")
                    if not "flags" in done:
                        if "flags" in add_parameters:
                            pass
                        else:
                            pass
                        pass
                    else:
                        print ("repeated 'flags' argument, you suck")
                else:
                    err ("unrecognized parameter, you suck")
            print (text)
            choicenumber = 0
            for choice in choices:
                choicenumber += 1
                print (str(choicenumber) + ": " + choice)
            choose = input ("> ")
            saved = False
            if choose.lower() in ("s", "save"):
                saved = True
                print ("Saved! (but not really)")
            while not choose.lower() in strrange(choicenumber):
                choose = input("> ")
                if choose.lower() in ("s", "save"):
                    if saved:
                        print ("You have already saved in this choice!")
                    else:
                        print ("Saved! (but not really)")
                        saved = True
            info.pointer = gotos[int(choose)]
            continue
        else:
            result = check_commands(info, line)
            if not result:
                show(line)
        info.pointer += 1
        if status.startswith("ending"):
            return " ".join(status.split(" ")[1:])
    raise exceptions.ScriptEndException()

# async def asyncparse() --- should finish standard parse first