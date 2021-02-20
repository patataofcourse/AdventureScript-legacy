from adventurescript import commands, exceptions
from adventurescript.inventory import Inventory

# This function takes a string and does a sort of eval() with it, but using AS' variables, flags and lists;
# and also counts the #.# expressions using AS' own values (so, #.int, for example).
async def input_format(info, text):
    # Warning: badly named variables ahead
    flip_result = False
    while text.startswith("-"):
        flip_result = not flip_result
        text = text[1:]
    if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')): #dirtiest fix ever
        text = [text]
    else:
        text = text.split("+")
    text2 = text + [] # text2 is used as a way to store the text through the loop, so like a temp variable
    c = 0
    for item in text:
        if c != 0:
            text2.insert(c, "+")
            c += 1
        c += 1
    text = text2 
    text2 = []
    operations1= []
    for item in text:
        if (item.startswith("'") and item.endswith("'")) or (item.startswith('"') and item.endswith('"')): #aaaaaaa
            text2 = text #dirtiest fix ever
            continue
        if item == "+":
            operations1.append(item)
        else:
            item = item.strip().split("-")
            c = 0
            for subitem in item:
                if c != 0:
                    operations1.append("-")
                text2.append(subitem.strip())
                c += 1
    text = text2
    text2 = []
    operations2 = []
    for item in text:
        if (item.startswith("'") and item.endswith("'")) or (item.startswith('"') and item.endswith('"')):
            text2.append([item]) #dirtiest fix ever
            continue
        operations2.append([])
        item = item.split("*")
        item2 = item
        c = 0
        for subitem in item:
            if c != 0:
                item2.insert(c, "*")
                c += 1
            c += 1
        item = item2 + []
        item2 = []
        for subitem in item:
            if subitem == "*":
                operations2[-1].append(subitem)
            else:
                subitem = subitem.strip().split("/")
                c = 0
                for subsubitem in subitem: #oh fuck
                    if c != 0:
                        operations2[-1].append("//")
                    item2.append(subsubitem.strip())
                    c += 1
        text2.append(item2)
    text = text2
    text2 = []
    operations3 = []
    for item in text:
        operations3.append([])
        item2 = []
        for subitem in item:
            if (subitem.startswith("'") and subitem.endswith("'")) or (subitem.startswith('"') and subitem.endswith('"')):
                item2.append([subitem]) #dirtiest fix ever
                operations1 = []
                operations2 = [[]]
                operations3 = [[[]]]
                continue
            operations3[-1].append([])
            subitem = subitem.split("^")
            c = 0
            for subsubitem in subitem:
                if c != 0:
                    operations3[-1][-1].insert(c, "**")
                    c += 1
                c += 1
            item2.append(subitem)
        text2.append(item2)
    text = text2
    text2 = []
    for item in text:
        item2 = []
        for subitem in item:
            subitem2 = []
            for subsubitem in subitem:
                    value = subsubitem.split(".")[0]
                    value_type = ""
                    ops = subsubitem.split(".")[1:]
                if value.isdecimal():
                    value = int(value)
                elif (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
                    value = value.strip("'\"").replace("\\n","\n")
                elif value.startswith("{") and value.endswith("}"):
                    value = find_label(info, value)
                # elif value.startswith("(") and value.endswith(")"): #TODO: Add this. Not gonna be needed for now
                #     value = eval(f"[+{value[1:-1]}]")
                elif value.startswith("$"):
                    value = info.lists[value[1:]]
                elif value.startswith("%"):
                    val = info.flags.get(value[1:], None)
                    if val == None:
                        val = False
                        info.flags[value[1:]] = False
                    value = val
                elif value.startswith("&"):
                    if value.startswith("&&"):
                        try:
                            value = info.inventory
                        except AttributeError:
                            raise Exception("No default inventory!") #TODO
                    else:
                        try:
                            value = info.extrainvs[value[1:]]
                        except NameError:
                            raise exceptions.UndefinedInventoryError(info.scriptname, info.pointer+1, inventory)
                elif value.lower() in ("true", "false"):
                    if value.lower() == "true":
                        value = True
                    else:
                        value = False
                else:
                    value = info.variables[value]
                    value = str(value)
                subitem2.append(await manage_operations(value, ops))
            subitem = subitem2
            subitem2 = subitem.pop(0)
            if len(subitem) != 0:
                for operation in operations3[0][0]:
                    subitem2 = str_but_quotes(eval(subitem2+operation+subitem.pop(0)))
            item2.append(subitem2)
            operations3[0].pop(0)
        operations3.pop(0)
        item = item2
        item2 = item.pop(0)
        if len(item) != 0:
            for operation in operations2[0]:
                item2 = str_but_quotes(eval(item2+operation+item.pop(0)))
        operations2.pop(0)
        text2.append(item2)
    text = text2
    text2 = text.pop(0)
    if len(text) != 0:
        for operation in operations1:
            text2 = str_but_quotes(eval(text2+operation+text.pop(0)))
    if flip_result:
        try:
            return -eval(text2)
        except TypeError as e:
            if str(e).split(":")[0] != "bad operand type for unary -":
                raise e
            else:
                raise Exception("well someone tried to - a non minusable thing")
    else:
        return eval(text2)

async def manage_operations(value, ops, quotes=True):
    for op in ops:
        if op == "str": #TODO: use a switchcase or something *better* please ffs
            value = str(value)
        elif op == "int":
            value = int(value) #TODO: Exception
        elif op == "list":
            try:
                value = list(value)
            except TypeError:
                value = [value]
        elif op == "flag":
            if value.lower == "false":
                value = False
            value = bool(value) # I do not know how bool() works, but it's probably stupid enough to be used in AS
        elif op.split("(")[0] == "elmt" and op.endswith(")") and op.split("(")[1][:-1].isdecimal():
            if type(value) == type([]):
                value = value[int(op.split("(")[1][:-1])]
            else:
                raise TypeError("Operation 'elmt' can only be used with lists")
        elif op == "ul":
            if type(value) == type([]):
                out = ""
                for item in value:
                    out += f"•{item}\n"
                value = out.strip()
            else:
                raise TypeError("Operation 'ul' can only be used with lists")
        elif op == "ol":
            if type(value) == type([]):
                out = ""
                c = 1
                for item in value:
                    out += f"{c}- {item}\n"
                    c += 1
                value = out.strip()
            else:
                raise TypeError("Operation 'ol' can only be used with lists")
        elif op == "money":
            if type(value) == Inventory:
                value = value.money
            else:
                raise TypeError("Operation 'ol' can only be used with lists")
        elif op == "not":
            if type(value) == bool:
                value = not value
            else:
                raise TypeError("Operation 'not' can only be used with flags")
        else:
            raise Exception(f"Invalid operation '{op}'!") #TODO
        ops.pop(0)
    if quotes:
        return str_but_quotes(value)
    else:
        return value

def str_but_quotes(value):
    if type(value) == str:
        return f"'''{value}'''"
    else:
        return str(value)

async def check_commands(info, line):
    line = line.strip()
    if line.startswith("{"):
        line = line[line.find("}")+1:]
        line = line.lstrip()

    if line == "":
        return False
    elif line.startswith("[") and line.endswith("]"):
        line = line[1:-1].split(";")
        line = [line[0].split(" ")[0], " ".join(line[0].split(" ")[1:])] + line[1:]
        for command in info.commands:
            if type(info.commands[command]) == type(str_but_quotes):
                if command == line[0]:
                    command = info.commands[command]
                    kwargs = {}
                    if line[1] == "":
                        await command(info)
                        return True
                    try:
                        for pair in line[1:]:
                            pair = pair.split("=")
                            kwargs[pair[0].strip()] = await input_format(info,"=".join(pair[1:]))
                    except Exception as e:
                        if type(e).__name__.split(".")[0] != "adventurescript":
                            raise exceptions.ArgumentSyntaxError(info.scriptname, info.pointer, line[0], e)
                        else:
                            raise e()
                    try:
                        await command(info, **kwargs)
                    except Exception as e:
                        if type(e).__name__.split(".")[0] != "adventurescript":
                            raise exceptions.CommandException(info.scriptname, info.pointer, line[0], e)
                        else:
                            raise e()
                    return True
        return False
    elif line.endswith("[n]"):
        line = line[:-3]
        await info.show(line)
        await commands.n(info)
        return True
    else:
        return False

def find_label(info, label):
    for line in info.script:
        if line.strip().startswith(label):
            return info.script.index(line)+1
    raise Exception(f"Label '{label}' not found!") #TODO

def remove_strings(text):
    #get the start and end of every string
    quotepos = [] #here we'll store the index of every quote that's not been escaped
    for quote in ("'", "\""):
        allpos = [i for i in range(len(text)) if text.startswith(quote, i)] #gets all instances of each type of quotes
        for index in allpos:
            if text[index-1] != "\\":
                quotepos.append(index) #only pass to quotepos the strings that weren't escaped
    opened_quote = ""
    quotes = []
    for index in sorted(quotepos):
        if opened_quote == "": #no open quotes
            opened_quote = text[index]
            quotes.append(index)
        elif opened_quote == text[index]:       #current quote is the same as the open quote -> it closes, and
            quotes[-1] = (quotes[-1], index)    #otherwise it just gets ignored and treated as any other character
            opened_quote = ""
    #now, replace them with things that won't be screwed up by the rest of input_format
    quotes.reverse() #this way the index numbers don't get fucked up
    c = 1
    quotetext = []
    for quote in quotes:
        quotetext = [text[quote[0]+1:quote[1]]] + quotetext
        text = text[:quote[0]] + f'"{len(quotes)-c}"' + text[quote[1]+1:]
        c += 1
    outquotes = [i.replace("\\'", "'").replace('\\"', '"') for i in quotetext] #gets all instances of each type of quotes
    return text, outquotes