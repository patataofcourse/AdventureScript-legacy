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
            raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "choice", kwarg)
    if not chs == gos or len(chs) != max(chs):
        raise exceptions.ChoiceArgumentError(info.scriptname, info.pointer)
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
    result = await info.query(text, choices, **kwargs)
    if result == 0: #TODO: i think this means that if the go_ is 0, it just continues without going. this is confusing though?
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

async def chaincheck(info, check1, go1, **kwargs):
    chs = [1]
    gos = [1]
    for kwarg in kwargs:
        if kwarg.startswith("check"):
            chs.append(int(kwarg[2:]))
        elif kwarg.startswith("go"):
            gos.append(int(kwarg[2:]))
        else:
            raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "chaincheck", kwarg)
    if not chs == gos or len(chs) != max(chs):
        raise exceptions.CheckArgumentError(info.scriptname, info.pointer)
    chs.sort()
    checks = [ch1]
    gotos = [go1]
    for item in chs[1:]:
        checks.append(kwargs["check"+str(item)])
        gotos.append(kwargs["go"+str(item)])
    while "" in gotos:
        checks.pop(checks.index(""))
        gotos.pop(gotos.index(""))
    c = 0
    for flag in checks:
        if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
           info.flags[flag] = False
           continue
        if info.flags[flag]:
            await goto(info, gotos[c])
            return
        c += 1
    #this will only happen if no check has happened
    if kwargs.get("godefault") == None:
        raise exceptions.MissingArgumentError(info.scriptname, info.pointer, "chaincheck", "godefault") #TODO:MissingOptionalArgumentWhichIsNeededHere
    await goto(info, godefault)

async def flag(info, **kwargs):
    for kwarg in kwargs:
        for character in kwarg:
            if character in info.forbidden_characters:
                raise exceptions.InvalidNameCharacter(info.scriptname, info.pointer, "flag", character)
        info.flags[kwarg] = kwargs[kwarg]

setflag = flag #viva le alias

async def delflag(info, flag):
    try:
        info.flags.pop(flag)
    except KeyError:
        raise exceptions.UndefinedFlagError(info.scriptname, info.pointer+1, flag)

#Variable commands

async def var(info, **kwargs):
    for kw in kwargs:
        for character in kw:
            if character in info.forbidden_characters:
                raise exceptions.InvalidNameCharacter(info.scriptname, info.pointer, "flag", character)
        info.variables[kw] = kwargs[kw]

setvar = var
defvar = var

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

#TODO: fix the switchcase you moron
async def switch(info, var, default=None, **kwargs): #hehe i actually did a switchcase
    for kw in kwargs:
        if str(var).strip('"') == kw: #TODO: str(var).strip('"') is a terrible idea, fix everywhere
            info.pointer = kwargs[kw]-1
            return
    if default==None:
        raise exceptions.CommandException(info.scriptname, info.pointer, "switch", "Missing 'default' argument")
    info.pointer= default-1

async def incvar(info, var, value): #basically +=
    info.variables[var] += value

async def delvar(info, var):
    try:
        info.variables.pop(var)
    except KeyError:
        raise exceptions.UndefinedVariableError(info.scriptname, info.pointer+1, var)

#List commands

async def deflist(info, list):
    for character in list:
        if character in info.forbidden_characters:
            raise Exception (f"Character '{character}' can't be used in a list name")
    info.lists[list] = []

list = deflist #careful: this alias might not work well

async def append(info, list, element):
    info.lists[list].append(element)

addlist = append

async def remove(info, list, element, find="pos"):
    if find == "pos":
        info.lists[list].pop(int(element))
    elif find == "name":
        info.lists[list].pop(info.lists[list].index(element))
    else:
        raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "remove", "find") #TODO: actual exception type for this

rmvlist = remove

async def checklist(info, list, element, gotrue, gofalse):
    if element in info.lists[list]:
        await goto(info, gotrue)
    else:
        await goto(info, gofalse)

listfind = checklist
chklist = checklist

async def dellist(info, list):
    try:
        info.lists.pop(list)
    except KeyError:
        raise exceptions.UndefinedListError(info.scriptname, info.pointer+1, list)

#Inventory commands

async def definv(info, inventory, size):
    for character in inventory:
        if character in info.forbidden_characters:
            raise exceptions.InvalidNameCharacter(info.scriptname, info.pointer, "inventory", character)
    info.extrainvs[inventory] = Inventory(size)

inv = definv

async def invadd(info, item, gofail, amount=1, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.add(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].add(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(info, gofail)
    elif gosuccess != None:
        await goto(info, gosuccess)

async def invrmv(info, item, gofail, amount=1, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.remove(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].remove(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(info, gofail)
    elif gosuccess != None:
        await goto(info, gosuccess)

async def invfind(info, item, gotrue, gofalse, amount=1, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.find(item, amount)
    else:
        try:
            res = info.extrainvs[inventory].find(item, amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if res == None:
        await goto(info, gofalse)
    else:
        await goto(info, gotrue)

checkinv = invfind
chkinv = invfind

async def invupgrade(info, size, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        info.inventory.upgrade(size)
    else:
        try:
            info.extrainvs[inventory].upgrade(size)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)

async def invdowngrade(info, size, gofail, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.downgrade(size)
    else:
        try:
            res = info.extrainvs[inventory].downgrade(size)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if res == 1 and gosuccess != None:
        await goto(info, gosuccess)
    elif res == 0:
        await goto(info, gofail)
    elif res == -1:
        raise NotImplementedError("Inventory management when it gets too small for you will be added here") #TODO

async def addmoney(info, amount, inventory=None): #I will add gofail/gosuccess to this one whenever I make wallet limits a thing. If I do.
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        info.inventory.money += amount
    else:
        try:
            info.extrainvs[inventory].money += amount
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)

async def rmvmoney(info, gofail, amount, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.remove_money(amount)
    else:
        try:
            res = info.extrainvs[inventory].remove_money(amount)
        except NameError:
            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
    if not res:
        await goto(info, gofail)
    elif gosuccess != None:
        await goto(info, gosuccess)

async def chkmoney(info, amount, gotrue, gofalse, inventory=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        inventory = info.inventory
    if inventory.money >= amount:
        info.pointer = gotrue-1
    else:
        info.pointer = gofalse-1

checkmoney = chkmoney

async def buy(info, item, price, gofail, amount=1, inventory=None): #Buy/sell commands to make my job simpler lol
    pass

async def sell(info, item, price, gofail, amount=1, inventory=None):
    pass

async def delinv(info, inv):
    try:
        info.extrainvs.pop(inv)
    except KeyError:
        raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inv)