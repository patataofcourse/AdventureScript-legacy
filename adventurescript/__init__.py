import asyncio
from adventurescript import commands, exceptions, defaultio, inventory, parsecmd
from adventurescript.info import ContextInfo
import os
import platform

async def parse(name, save_id=0, show=defaultio.show, wait=defaultio.wait, query=defaultio.query, pass_info = False, addons = [], is_async=False, load_file=defaultio.load_file):
    info = ContextInfo(name, save_id, show, wait, query, is_async, pass_info, load_file)
    
    #Load addons
    for addon in addons: #TODO: rework addons
        try:
            addon.setup(info)
            for command in addon.commands:
                info.commands[command.__name__] = command
        except Exception as e:
            print (f"Exception while attempting to add addon {addon.__name__}:", e)

    #Prompt to restore last save
    try:
        save = open(f"games/{info.gamename}/save/{info.save_id}.asv").read().split("}{")
    except:
        pass
    else:
        await info.show("A save file has been detected. Would you like to restore it?")
        response = await info.query("",("Yes", "No"), False)
        if response == 2:
            await info.show("A new game will be started.")
            await info.wait()
        else:
            info.reload()
            info.pointer += 1
    
    #The actual parsing
    while info.pointer <= len(info.script):
        line = info.script[info.pointer-1].rstrip()
        if not line.startswith("#"):
            result = await parsecmd.check_commands(info, line)
            if not result:
                await info.show(line)
        info.pointer += 1
        if info.status == "ok":
            pass
        elif info.status.startswith("ending") or info.status.startswith("quit"):
            return info.status
        else:
            raise Exception("Unknown status!") #TODO
    raise exceptions.ScriptEndException(info.scriptname)

def parse_sync(*args):
    return asyncio.run(parse(*args))