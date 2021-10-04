from adventurescript import commands, exceptions, func, operations
from adventurescript.inventory import Inventory

import builtins
import re

# This function takes a string and does a sort of eval() with it, but using AS' variables, flags and lists;
# and also counts the X.Y expressions using AS' own values (so, "3".int, for example).
async def evaluate(info, text):
    # Warning: badly named variables ahead
    flip_result = False
    text = text.strip()
    while text.startswith("-"):
        flip_result = not flip_result
        text = text[1:]
    
    text, outquotes = func.remove_strings(text)
    text, outlabels = compress_labels(info, text)

    operators = re.findall("\+|\-|\*|\/|\^", text)
    raw_values = re.split("\+|\-|\*|\/|\^", text)

    operators = ["**" if i=="^" else i for i in operators]
    operators = ["//" if i=="/" else i for i in operators]

    values = []
    for value in raw_values:
        value, *ops = value.strip().split(".")
        
        #literals
        if value.isdecimal(): #int literal
            value = int(value)
        elif value.lower() == "true": #bool literal: true
            value = True
        elif value.lower() == "false": #bool literal: false
            value = False
        elif value.startswith('"') and value.endswith('"'): #string literal
            value = outquotes[int(value.strip('"'))]
        elif value.startswith("{") and value.endswith("}"): #label literal
            value = outlabels[int(value.strip("{}"))]
        
        #saved variables
        elif value.startswith("$"): #list
            value = info.list(value[1:])
        elif value.startswith("%"): #flag
            val = info.flags.get(value[1:], None)
            if val == None:
                val = False
                info.flags[value[1:]] = False
            value = val
        elif value.startswith("&"): #inventory
            if value.startswith("&&"): #default inventory
                try:
                    value = info.inventory
                except AttributeError:
                    raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer+1)
            else:
                value = info.inv(value[1:])
        else: #values
            value = info.var(value)
        values.append(repr(await operations.manage_operations(value, ops)))

    for op_groups in ["**"], ["*", "//"], ["+", "-"]:
        c = 0
        while c < len(operators):
            if operators[c] in op_groups:
                op = operators[c]
                operators.pop(c)
                values[c] = repr(eval(values[c]+op+values[c+1]))
                values.pop(c+1)
            else:
                c += 1
    
    if flip_result:
        return -eval(values[0])
    else:
        return eval(values[0])

async def check_commands(info, line):
    line = line.strip()
    if line.startswith("{"):
        line = line[line.find("}")+1:]
        line = line.lstrip()

    if line == "":
        return False
    elif line.startswith("!"):
        line = line[1:].strip().split(";")
        line = [line[0].split(" ")[0], " ".join(line[0].split(" ")[1:])] + line[1:]
        for command in info.commands:
            if type(info.commands[command]) == builtins.function:
                if command == line[0]:
                    command = info.commands[command]
                    kwargs = {}
                    if line[1] == "":
                        await command(info)
                        return True
                    try:
                        for pair in line[1:]:
                            pair = pair.split("=")
                            kwargs[pair[0].strip()] = await evaluate(info,"=".join(pair[1:]))
                    except Exception as e:
                        if type(e) == exceptions.ArgumentSyntaxError:
                            raise e
                        raise exceptions.ArgumentSyntaxError(info.scriptname, info.pointer+1, e)
                    
                    try:
                        #insert here checking the args
                        #TODO: figure out what i meant by that ^
                        await command(info, **kwargs)
                    except Exception as e:
                        if type(e) == exceptions.CommandException:
                            raise e
                        raise exceptions.CommandException(info.scriptname, info.pointer+1, e)
                    return True
        raise exceptions.UndefinedCommandError(info.scriptname, info.pointer+1, line[0])
    elif line.endswith("\i"):
        line = line[:-2]
        await info.show(line)
        await commands.n(info)
        return True
    else:
        return False

def find_label(info, label):
    for ch in info.forbidden_characters:
        if ch in label[1:-1]:
            raise exceptions.InvalidNameCharacter(info.scriptname, info.pointer+1, "label", ch)
    for line in info.script:
        if line.strip().startswith("{" + label + "}"):
            return info.script.index(line)+1
    raise exceptions.UndefinedLabelError(info.scriptname, info.pointer+1, label)

def compress_labels(info, text): #latter half stolen from remove_strings
    start = None
    labels = []
    c = 0
    for char in text:
        if start == None and char == "{":
            start = c
        elif start != None and char == "}":
            labels.append((start, c))
            start = None
        c += 1
    if start != None:
        raise SyntaxError("AdventureScript syntax: unclosed {")
    
    #now, replace them with things that won't be screwed up by the rest of evaluate
    labels.reverse() #this way the index numbers don't get fucked up
    c = 1
    outlabels = []
    for label in labels:
        outlabels = [text[label[0]+1:label[1]]] + outlabels
        text = text[:label[0]]  + "{" + str(len(labels)-c) + "}" +  text[label[1]+1:] #"0", "1", etc.
        c += 1
    outlabels = [find_label(info, i) for i in outlabels] #gets the positions of the labels
    return text, outlabels