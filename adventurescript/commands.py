def n(info):
    info.wait()
    info.pointer += 1

def goto(info, pos, **kwargs): #TODO
    pass

def choice(info, ch1, go1, flags=None, **kwargs): #TODO
    pass

def loadscript(info, name):
    info.script = open(f"../{name}.adv")
    info.pointer = 0

def flags(info, **kwargs):
    for kwarg in kwargs:
        info.flags[kwarg] = kwargs[kwarg]

def ending(info, name):
    info.ending(name)

commands = [n, goto, choice, loadscript, flags, ending]