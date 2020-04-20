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
    if flags != None:
        info.show("Warning: 'flags' argument in choice not implemented") #TODO: Implement this
    chs.sort()
    choices = [ch1]
    gotos = [go1]
    for item in chs[1:]:
        choices.append(kwargs["ch"+str(item)])
        gotos.append(kwargs["go"+str(item)])
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
    info.script = open(f"{name}.adv").read().split("\n")
    info.pointer = 1

def flag(info, **kwargs):
    for kwarg in kwargs: #TODO: add bool checking
        info.flags[kwarg] = kwargs[kwarg].lower()

def ending(info, name):
    info.ending(name)

commands = [n, goto, choice, loadscript, flag, ending, checkflag]