import asyncio
from adventurescript import commands, exceptions, defaultio, parsecmd
from adventurescript.info import ContextInfo
import os
import platform

class Inventory:
    def __init__(self, size, start_items={}, money=0):
        if size == 0:
            raise Exception("Inventory size cannot be 0") #TODO
        if len(start_items) > size:
            raise Exception("Inventory size too small for all the starting items given!") #TODO
        self.inv = [None]*size
        for item in start_items:
            self.add(item, start_items[item])
        self.money = money
    def find(self, item, min_quantity=1):
        for elmt in inventory:
            if item == elmt[0]:
                return inventory.index(elmt) if min_quantity <= elmt[1] else None
        return None
    def upgrade(self, plus_size):
        self.inv += [None] * plus_size
    def downgrade(self, minus_size):
        if len(self.inv) - minus_size == 0:
            raise Exception("Inventory size cannot be 0") #TODO
        elif self.inv.count(None) < minus_size:
            raise Exception("Trying to remove inventory size, but there's still some items in the portion to be removed") #TODO
        else:
            self.inv = self.inv[:len(self.inv)-minus_size]
    def add(self, item, quantity=1):
        item_in_inv = False
        for pair in self.inv:
            if pair != None and item == pair[0]:
                item_in_inv = True
                pos = self.inv.index(pair)
        if item_in_inv:
            self.inv[pos][1] += quantity
        else:
            try:
                empty_slot = self.inv.index(None)
            except ValueError:
                return False
            else:
                self.inv[empty_slot] = [item, quantity]
                return True
    def remove(self, item, quantity=1):
        pos = self.find(item, quantity)
        if pos == None:
            self.inv[pos][1] -= quantity
            if self.inv[pos][1] == 0:
                self.inv.pop(pos)
                self.inv.append(None)
    def represent(self):
        out = ""
        return out

async def parse(name, save_id=0, show=defaultio.show, wait=defaultio.wait, query=defaultio.query, pass_info = False, addons = [], is_async=False):
    info = ContextInfo(name, save_id, show, wait, query, is_async, pass_info)
    
    #Load addons
    for addon in addons:
        try:
            addon.setup(info)
            commands.commands += addon.commands
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
    print(info.scriptname, info.pointer)
    raise exceptions.ScriptEndException()

def parse_sync(*args):
    return asyncio.run(parse(*args))