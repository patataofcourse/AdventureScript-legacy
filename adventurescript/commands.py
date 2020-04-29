from adventurescript import exceptions

def n(info):
    info.wait()

def goto(info, pos):
    info.pointer = int(pos)-1

def choice(info, ch1, go1, text="", flags=None, **kwargs):
    chs = [1]
    gos = [1]
    for kwarg in kwargs:
        if kwarg.startswith("ch"):
            chs.append(int(kwarg[2:]))
        elif kwarg.startswith("go"):
            gos.append(int(kwarg[2:]))
        else:
            raise Exception("Unwanted argument in choice command") #TODO: use the proper exception
    if not chs == gos or len(chs) != max(chs):
        raise Exception("You screwed up somewhere with the chs and gos in a choice command") #TODO: use the proper exception
    flagdict = {}
    if flags != None:
        flags = flags.strip("{}").split(",")
        for flag in flags:
            if int(flag.split(":")[0]) in flagdict:
                raise Exception("Choice number mentioned twice in flag argument of choice command")
            elif info.flags.get(flag.split(":")[1], None) == None: #If the flag doesn't exist, it immediately gets set as false
                info.flags[flag.split(":")[1]] = False
            elif info.flags[flag.split(":")[1]] == "true":
                flagdict[int(flag.split(":")[0])] = True
            else:
                flagdict[int(flag.split(":")[0])] = False
    chs.sort()
    choices = [ch1]
    gotos = [go1]
    for item in chs[1:]:
        choices.append(kwargs["ch"+str(item)])
        gotos.append(kwargs["go"+str(item)])
    for flag in flagdict:
        if not flagdict[flag]:
            choices.pop(flag-1)
            gotos.pop(flag-1)
    result = ""
    while result in ("r", "s", ""):
        result = info.query(text, choices)
        if result == "s":
            info.show("Saved! (But not really)")
        elif result == "r":
            info.show("This would restore the save")
    goto(info, gotos[int(result)-1])


def checkflag(info, flag, gotrue, gofalse):
    if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
        info.flags[flag] = False

    if info.flags[flag] == "true":
        info.pointer = int(gotrue)-1
    else:
        info.pointer = int(gofalse)-1

def loadscript(info, name):
    info.scriptname = name
    info.script = open(f"{name}.adv").read().split("\n")
    info.pointer = 1

def flag(info, **kwargs):
    for kwarg in kwargs:
        if kwargs[kwarg].lower() in ("true", "false"):
            info.flags[kwarg] = kwargs[kwarg].lower()
        else:
            raise exceptions.NonBoolFlagException(info.scriptname, info.pointer+1, "flag", kwarg)

def ending(info, name):
    info.ending(name)

commands = [n, goto, choice, loadscript, flag, ending, checkflag]