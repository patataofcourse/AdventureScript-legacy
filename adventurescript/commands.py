from adventurescript import exceptions

async def n(info):
    await info.wait()

async def goto(info, pos):
    info.pointer = int(pos)-1

async def choice(info, ch1, go1, text="", flags=None, **kwargs):
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
                flagdict[int(flag.split(":")[0])] = False
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
    result = await info.query(text, choices)
    if result == 0:
        return
    await goto(info, gotos[int(result)-1])

async def checkflag(info, flag, gotrue, gofalse):
    if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
        info.flags[flag] = False

    if info.flags[flag] == "true":
        info.pointer = int(gotrue)-1
    else:
        info.pointer = int(gofalse)-1

async def loadscript(info, name, pos=1):
    info.scriptname = f"script/{info.gamename}/{name}"
    info.script = open(f"{info.scriptname}.asf").read().split("\n")
    info.pointer = pos

async def flag(info, **kwargs):
    for kwarg in kwargs:
        if kwargs[kwarg].lower() in ("true", "false"):
            info.flags[kwarg] = kwargs[kwarg].lower()
        else:
            raise exceptions.NonBoolFlagException(info.scriptname, info.pointer+1, "flag", kwarg)

async def ending(info, name):
    info.ending(name)

async def saveoff(info):
    info.allow_save = False

async def saveon(info):
    info.allow_save = True

async def setvar(info, **kwargs):
    for kw in kwargs:
        #can't be bothered to number check, i'll do that in __init__.py
        info.variables[kw] = kwargs[kw]

async def checkvar(info, var, value, gotrue, gofalse, comparison="equal"):
    if var not in info.variables:
        raise exceptions.UndefinedVariableError(info.scriptname, info.pointer+1, "checkvar", var)
    if comparison.lower() in ("equal", "=", "==", "==="):
        result = info.variables[var] == value
    elif comparison.lower() in ("greater", ">"):
        result = info.variables[var] > value
    elif comparison.lower() in ("greater or equal", ">="):
        result = info.variables[var] >= value
    elif comparison.lower() in ("lesser", "<"):
        result = info.variables[var] < value
    elif comparison.lower() in ("lesser or equal", "<="):
        result = info.variables[var] <= value
    else:
        raise exceptions.CommandException(info.scriptname, info.pointer+1, "checkvar", f"Invalid comparison type: {comparison}")
    if result:
        info.pointer = int(gotrue)-1
    else:
        info.pointer = int(gofalse)-1

async def incvar(info, var, value): #basically +=
    pass

async def deflist(info, list):
    info.lists[list] = []

async def append(info, list, element):
    info.lists[list].append(element)

async def remove(info, list, element, find="pos"):
    if find == "pos":
        info.lists[list].pop(int(element))
    elif find == "name":
        info.lists[list].pop(list.find(element, None))
    else:
        Exception() #TODO

async def checklist(info, list, element, gotrue, gofalse):
    if element in info.lists[list]:
        await goto(info, gotrue)
    else:
        await goto(info, gofalse)

commands = [n, goto, choice, loadscript, flag, ending, saveoff, saveon, checkflag, setvar, checkvar, deflist, append, remove, checklist] #, incvar