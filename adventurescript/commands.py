def n(info):
    info.wait()

def goto(info, pos):
    info.pointer = int(pos)-1

def choice(info, ch1, go1, flags=None, **kwargs): #TODO
    pass

def loadscript(info, name):
    info.script = open(f"{name}.adv").read().split("\n")
    info.pointer = 1

def flag(info, **kwargs):
    for kwarg in kwargs:
        info.flags[kwarg] = kwargs[kwarg]

def ending(info, name):
    info.ending(name)

commands = [n, goto, choice, loadscript, flag, ending]