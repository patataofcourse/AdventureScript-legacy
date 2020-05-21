from adventurescript import exceptions

async def n(info):
    await info.wait()

async def goto(info, pos):
    info.pointer = int(pos)-1

async def choice(info, ch1, go1, text="", **kwargs):
    chs = [1]
    gos = [1]
    flags = []
    for kwarg in kwargs:
        if kwarg.startswith("ch"):
            chs.append(int(kwarg[2:]))
        elif kwarg.startswith("go"):
            gos.append(int(kwarg[2:]))
        elif kwarg.startswith("flag"):
            flags.append(int(kwarg[4:]))
        else:
            raise Exception("Unwanted argument in choice command") #TODO: use the proper exception
    if not chs == gos or len(chs) != max(chs):
        raise Exception("You screwed up somewhere with the chs and gos in a choice command") #TODO: use the proper exception
    flagdict = {}
    for flag in flags:
        flagdict[flag] = kwargs["flag"+str(flag)]
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
    if info.flags[flag]:
        info.pointer = int(gotrue)-1
    else:
        info.pointer = int(gofalse)-1

async def loadscript(info, name, pos=1):
    info.scriptname = f"script/{info.gamename}/{name}"
    info.script = open(f"{info.scriptname}.asf").read().split("\n")
    info.pointer = pos

async def flag(info, **kwargs):
    for kwarg in kwargs:
        for character in kwarg:
            if character in info.forbidden_characters:
                raise Exception (f"Character '{character}' can't be used in a flag name")
        info.flags[kwarg] = kwargs[kwarg]

async def ending(info, name):
    info.ending(name)

async def saveoff(info):
    info.allow_save = False

async def saveon(info):
    info.allow_save = True

async def setvar(info, **kwargs):
    for kw in kwargs:
        for character in kw:
            if character in info.forbidden_characters:
                raise Exception (f"Character '{character}'' can't be used in a variable name")
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
    info.variables[var] += value

async def deflist(info, list):
    for character in list:
        if character in info.forbidden_characters:
            raise Exception (f"Character '{character}'' can't be used in a list name")
    info.lists[list] = []

async def append(info, list, element):
    info.lists[list].append(element)

async def remove(info, list, element, find="pos"):
    if find == "pos":
        info.lists[list].pop(int(element))
    elif find == "name":
        info.lists[list].pop(info.lists[list].index(element))
    else:
        Exception() #TODO

async def checklist(info, list, element, gotrue, gofalse):
    if element in info.lists[list]:
        await goto(info, gotrue)
    else:
        await goto(info, gofalse)

async def gameover(info):
    await info.show("**GAME OVER**")
    r = await info.query("Start over from last save?",("Yes","No"),False)
    if r == 1:
        info.reload()
    else:
        info.quit()

commands = [n, goto, choice, loadscript, flag, ending, saveoff, saveon, checkflag, setvar, checkvar, incvar, deflist, append, remove, checklist, gameover]