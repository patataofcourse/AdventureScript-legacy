import json

from adventurescript import exceptions
from adventurescript.inventory import Inventory

#General use commands

async def n(info):
    await info.wait()

pause = n

async def goto(info, pos):
    info.pointer = int(pos)-1

async def choice(info, ch1, go1=0, text="", **kwargs):
    chs = [1]
    gos = [1]
    flags = []
    for kwarg in kwargs:
        if kwarg.startswith("ch"):
            chs.append(int(kwarg[2:]))
        elif kwarg.startswith("go") and kwarg != "godefault":
            gos.append(int(kwarg[2:]))
        elif kwarg.startswith("flag"):
            flags.append(int(kwarg[4:]))
        elif kwarg != "godefault":
            raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "choice", kwarg)
    if len(chs) != max(chs) or max(chs) < max(gos):
        raise exceptions.ChoiceArgumentError(info.scriptname, info.pointer)
    flagdict = {}
    for flag in flags:
        flagdict[flag] = kwargs["flag"+str(flag)]
    chs.sort()
    choices = [ch1]
    gotos = [go1]
    for item in chs[1:]:
        choices.append(kwargs["ch"+str(item)])
        if item in gos:
            gotos.append(kwargs.get("go"+str(item)))
        else:
            gotos.append(0)
    
    for flag in flagdict:
        if not flagdict[flag]:
            choices[flag-1] = ""
            gotos[flag-1] = ""
    while "" in gotos:
        choices.pop(choices.index(""))
        gotos.pop(gotos.index(""))
    
    result = await info.query(text, choices, **kwargs)
    if result == 0: #for situations where a save/resume/quit is done
        return
    if kwargs.get("godefault") == None and gotos[int(result)-1] == 0:
        raise exceptions.MissingArgumentError(info.scriptname, info.pointer, "choice", "godefault") #TODO: MissingOptionalArgumentWhichIsNeededHere
    elif gotos[int(result)-1] == 0:
        await goto(info, kwargs["godefault"])
    else:
        await goto(info, gotos[int(result)-1])

async def loadscript(info, name, pos=1):
    info.scriptname = name
    info.script = info.load_script(name).split("\n")
    info.pointer = pos-1

async def gameover(info):
    await info.show("**GAME OVER**")
    r = await info.query("Start over from last save?",("Yes","No"),False)
    if r == 1:
        info.reload()
    else:
        info.quit()

async def ending(info, name):
    await info.wait()
    info.ending(name)

async def saveoff(info):
    info.allow_save = False

async def saveon(info):
    info.allow_save = True

#Flag commands

async def checkflag(info, flag, gotrue, gofalse):
    if type(flag) == str: #TODO: warn that it's deprecated
        if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
            info.flags[flag] = False
        flag = info.flags[flag]
    if flag:
        info.pointer = gotrue-1
    else:
        info.pointer = gofalse-1

async def chaincheck(info, check1, go1, **kwargs):
    chs = [1]
    gos = [1]
    for kwarg in kwargs:
        if kwarg.startswith("check"):
            chs.append(int(kwarg[5:]))
        elif kwarg.startswith("go") and kwarg != "godefault":
            gos.append(int(kwarg[2:]))
        elif kwarg != "godefault":
            raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "chaincheck", kwarg)
    if not chs == gos or len(chs) != max(chs):
        raise exceptions.CheckArgumentError(info.scriptname, info.pointer)
    chs.sort()
    checks = [check1]
    gotos = [go1]
    for item in chs[1:]:
        checks.append(kwargs["check"+str(item)])
        gotos.append(kwargs["go"+str(item)])
    c = -1
    for flag in checks:
        c += 1
        if info.flags.get(flag, None) == None: #If the flag doesn't exist, it immediately gets set as false
            info.flags[flag] = False
            continue
        if info.flags[flag]:
            await goto(info, gotos[c])
            return
    #this will only happen if no check has happened
    if kwargs.get("godefault") == None:
        raise exceptions.MissingArgumentError(info.scriptname, info.pointer, "chaincheck", "godefault") #TODO: MissingOptionalArgumentWhichIsNeededHere
    await goto(info, kwargs["godefault"])

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
        result = info.var(var) == value
    elif comparison.lower() in ("greater", ">"):
        result = info.var(var) > value
    elif comparison.lower() in ("greater or equal", ">="):
        result = info.var(var) >= value
    elif comparison.lower() in ("lesser", "<"):
        result = info.var(var) < value
    elif comparison.lower() in ("lesser or equal", "<="):
        result = info.var(var) <= value
    else:
        raise exceptions.CommandException(info.scriptname, info.pointer+1, "checkvar", f"Invalid comparison type: {comparison}")
    if result:
        info.pointer = gotrue-1
    else:
        info.pointer = gofalse-1

async def switch(info, var, case1, go1, **kwargs): #hehe i actually did a switchcase
    cas = [1]
    gos = [1]
    for kwarg in kwargs:
        if kwarg.startswith("case"):
            cas.append(int(kwarg[4:]))
        elif kwarg.startswith("go") and kwarg != "godefault":
            gos.append(int(kwarg[2:]))
        elif kwarg != "godefault":
            raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "chaincheck", kwarg)
    if not cas == gos or len(cas) != max(cas):
        raise exceptions.SwitchArgumentError(info.scriptname, info.pointer)
    cas.sort()
    cases = [case1]
    gotos = [go1]
    for item in cas[1:]:
        cases.append(kwargs["case"+str(item)])
        gotos.append(kwargs["go"+str(item)])
    for case in cases: #i know this is unnecessary but i'm keeping it for consistency
        if var == case:
            info.pointer = gotos[cases.index(case)]-1
            return
    if kwargs.get("godefault") == None:
        raise exceptions.MissingArgumentError(info.scriptname, info.pointer, "switch", "godefault") #TODO: MissingOptionalArgumentWhichIsNeededHere
    info.pointer = kwargs["godefault"]-1

async def incvar(info, var, value): #basically +=
    if info.variables.get(var) == None:
        raise UndefinedVariableError(info.scriptname, info.pointer+1, var)
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
    info.list(list).append(element)

addlist = append

async def remove(info, list, element, find="pos"):
    if find == "pos":
        info.list(list).pop(int(element))
    elif find == "name":
        info.list(list).pop(info.list(list).index(element))
    else:
        raise exceptions.UnwantedArgumentError(info.scriptname, info.pointer, "remove", "find") #TODO: actual exception type for this

rmvlist = remove

async def checklist(info, list, element, gotrue, gofalse):
    if element in info.list(list):
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
    try:
        info.extrainvs[inventory] = Inventory(size)
    except exceptions.invsize():
         raise ZeroInventorySizeError(info.scriptname, info.pointer)

inv = definv

async def invadd(info, item, gofail, amount=1, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.add(item, amount)
    else:
        res = info.inv(inventory).add(item, amount)
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
        res = info.inv(inventory).remove(item, amount)
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
        res = info.inv(inventory).find(item, amount)
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
        info.inv(inventory).upgrade(size)

async def invdowngrade(info, size, gofail, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.downgrade(size)
    else:
        res = info.inv(inventory).downgrade(size)
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
        info.inventory.add_money(amount)
    else:
        info.inv(inventory).add_money(amount)

async def rmvmoney(info, gofail, amount, inventory=None, gosuccess=None):
    if inventory == None:
        if not hasattr(info, "inventory"):
            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
        res = info.inventory.remove_money(amount)
    else:
        res = info.inv(inventory).remove_money(amount)
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

#Achievement commands

async def achievement(info, name): #TODO: pls remove file i/o code from here, move it to info.py or something
    if name in info.achievements:
        return
    
    ach = None
    for a in info.gameinfo["achievements"]:
        if a["name"] == name:
            ach = a

    if ach == None:
        raise NonExistentAchievementError(info.scriptname, info.pointer+1)

    if ach.get("type", "flag") != "flag":
        raise NotImplementedError("Achievement types other than flag are not implemented in achievement command!")

    pers_save = json.loads(info.load_save(True))
    savep_file = info.load_save(True, "w")
    
    info.achievements.append(name)
    pers_save["achievements"] = info.achievements
    
    savep_file.write(json.dumps(pers_save))
    savep_file.close()
    
    await info.show(f"\n__[You just got the **{name}** achievement!]__\n")

#Chapter commands

async def chapter(info, name):
    info.chapter = name
    await loadscript(info, "start")