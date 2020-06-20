from adventurescript import exceptions
from adventurescript.inventory import Inventory

#General use commands

async def n(info):
    await info.wait()

pause = n

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
            choices[flag-1] = ""
            gotos[flag-1] = ""
    while "" in gotos:
        choices.pop(choices.index(""))
        gotos.pop(gotos.index(""))
    result = await info.query(text, choices)
    if result == 0:
        return
    await goto(info, gotos[int(result)-1])

async def loadscript(info, name, pos=1):
    info.scriptname = f"games/{info.gamename}/script/{name}"
    info.script = open(f"{info.scriptname}.asf").read().split("\n")
    info.pointer = pos-1

async def gameover(info):
    await info.show("**GAME OVER**")
    r = await info.query("Start over from last save?",("Yes","No"),False)
    if r == 1:
        info.reload()
    else:
        info.quit()

async def ending(info, name):
    info.ending(name)

async def saveoff(info):
    info.allow_save = False

async def saveon(info):
    info.allow_save = True

#Flag commands

async def checkflag(info, flag, gotrue, gofalse):
    if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
        info.flags[flag] = False
    if info.flags[flag]:
        info.pointer = gotrue-1
    else:
        info.pointer = gofalse-1

async def flag(info, **kwargs):
    for kwarg in kwargs:
        for character in kwarg:
            if character in info.forbidden_characters:
                raise Exception (f"Character '{character}' can't be used in a flag name") #TODO
        info.flags[kwarg] = kwargs[kwarg]

setflag = flag #viva le alias

#Variable commands

async def var(info, **kwargs):
    for kw in kwargs:
        for character in kw:
            if character in info.forbidden_characters:
                raise Exception (f"Character '{character} can't be used in a variable name") #TODO
        info.variables[kw] = kwargs[kw]

setvar = var

async def checkvar(info, var, value, gotrue, gofalse, comparison="equal"):
    if var not in info.variables:
        raise exceptions.UndefinedVariableError(info.scriptname, info.pointer+1, var)
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
        info.pointer = gotrue-1
    else:
        info.pointer = gofalse-1

async def switch(info, var, default=None, **kwargs): #hehe i actually did a switchcase
    for kw in kwargs:
        if str(var).strip('"') == kw:
            info.pointer = kwargs[kw]-1
            return
    if default==None:
        raise exceptions.CommandException(info.scriptname, info.pointer, "switch", "Missing 'default' argument")
    info.pointer= default-1

async def incvar(info, var, value): #basically +=
    info.variables[var] += value

#List commands

async def deflist(info, list):
    for character in list:
        if character in info.forbidden_characters:
            raise Exception (f"Character '{character}' can't be used in a list name")
    info.lists[list] = []

async def append(info, list, element):
    info.lists[list].append(element)

async def remove(info, list, element, find="pos"):
    if find == "pos":
        info.lists[list].pop(int(element))
    elif find == "name":
        info.lists[list].pop(info.lists[list].index(element))
    else:
        raise Exception() #TODO

async def checklist(info, list, element, gotrue, gofalse):
    if element in info.lists[list]:
        await goto(info, gotrue)
    else:
        await goto(info, gofalse)

listfind = checklist

#Inventory commands

async def definv(info, inventory, size):
    for character in inventory:
        if character in info.forbidden_characters:
            raise Exception (f"Character '{character}' can't be used in an inventory name") #TODO
    info.extrainvs[inventory] = Inventory(size)

async def invadd(info, item, gofail, amount=1, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise Exception("No default inventory preset! Check your game's info file!")
        res = info.inventory.add(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].add(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(gofail)
    elif gosuccess != None:
        await goto(gosuccess)

async def invrmv(info, item, gofail, amount=1, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise Exception("No default inventory preset! Check your game's info file!")
        res = info.inventory.remove(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].remove(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(gofail)
    elif gosuccess != None:
        await goto(gosuccess)

async def invfind(info, item, gotrue, gofalse, amount=1, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise Exception("No default inventory preset! Check your game's info file!")
        res = info.inventory.find(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].find(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(gofalse)
    elif gosuccess != None:
        await goto(gotrue)

checkinv = invfind

async def addmoney(info, amount, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise Exception("No default inventory preset! Check your game's info file!")
        info.inventory.money += amount
    else:
        try:
            info.extrainvs[inventory].money += amount
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)

async def rmvmoney(info, amount, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise Exception("No default inventory preset! Check your game's info file!")
        info.inventory.money -= amount
    else:
        try:
            info.extrainvs[inventory].money -= amount
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)

async def buy(info, item, price, gofail, amount=1, inventory=None): #Buy/sell commands to make my job simpler lol
    pass

async def sell(info, item, price, gofail, amount=1, inventory=None):
    pass