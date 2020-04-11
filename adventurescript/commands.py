from adventurescript import exceptions
def n(info):
    info.wait()

def goto(info, pos):
    info.pointer = int(pos)-1

def choice(info, ch1, go1, text="", flags=None, **kwargs): #TODO
    chs = [1]
    gos = [1]
    for kwarg in kwargs:
        if kwarg.startswith("ch"):
            chs.append(int(kwarg[2:]))
        elif kwarg.startswith("go"):
            gos.append(int(kwarg[2:]))
        else:
            raise Exception("Unwanted argument in choice command") #i don't feel like coding an entire exception
    if not chs == gos or len(chs) != max(chs):
        raise Exception("You screwed up somewhere with the chs and gos in a choice command") #same tbh
    if flags != None: #insert here flag checking
        info.show("Warning: 'flags' argument in choice not implemented")
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


def loadscript(info, name):
    info.script = open(f"{name}.adv").read().split("\n")
    info.pointer = 1

def flag(info, **kwargs):
    for kwarg in kwargs:
        info.flags[kwarg] = kwargs[kwarg]

def ending(info, name):
    info.ending(name)

commands = [n, goto, choice, loadscript, flag, ending]