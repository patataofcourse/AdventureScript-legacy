from adventurescript import commands, exceptions
from adventurescript.inventory import Inventory

# This function takes a string and does a sort of eval() with it, but using AS' variables, flags and lists;
# and also counts the #.# expressions using AS' own values (so, #.int, for example).
async def input_format(info, text):
    # Warning: badly named variables ahead
    flip_result = False
    text = text.lstrip()
    while text.startswith("-"):
        flip_result = not flip_result
        text = text[1:]
    
    text, outquotes = remove_strings(text)
    text, outlabels = compress_labels(info, text)

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
                # elif value.startswith("(") and value.endswith(")"): #TODO: Add this. Not gonna be needed for now
                #     value = eval(f"[+{value[1:-1]}]")
                elif value.startswith("$"):
                    value = info.list(value[1:])
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
                            raise exceptions.NoDefaultInventoryError(info.scriptname, info.pointer)
                    else:
                        value = info.inv(value[1:])
                elif value.lower() in ("true", "false"):
                    if value.lower() == "true":
                        value = True
                    else:
                        value = False
                elif value.startswith('"') and value.endswith('"'):
                    value = outquotes[int(value.strip('"'))]
                elif value.startswith("{") and value.endswith("}"):
                    value = outlabels[int(value.strip("{}"))]
                else:
                    value = info.var(value)
                subitem2.append(await manage_operations(value, ops))
            subitem = subitem2
            subitem2 = subitem.pop(0)
            if len(subitem) != 0:
                for operation in operations3[0][0]:
                    subitem2 = repr(eval(subitem2+operation+subitem.pop(0)))
            item2.append(subitem2)
            operations3[0].pop(0)
        operations3.pop(0)
        item = item2
        item2 = item.pop(0)
        if len(item) != 0:
            for operation in operations2[0]:
                item2 = repr(eval(item2+operation+item.pop(0)))
        operations2.pop(0)
        text2.append(item2)
    text = text2
    text2 = text.pop(0)
    if len(text) != 0:
        for operation in operations1:
            text2 = repr(eval(text2+operation+text.pop(0)))
    if flip_result:
        try:
            return -eval(text2)
        except TypeError as e:
            if str(e).split(":")[0] != "bad operand type for unary -":
                raise e
            else:
                raise Exception("well someone tried to - a non minusable thing") #TODO
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
                raise TypeError("Operation 'money' can only be used with inventories")
        elif op == "size":
            if type(value) == Inventory:
                value = value.size
            else:
                raise TypeError("Operation 'size' can only be used with inventories")
        elif op == "not":
            if type(value) == bool:
                value = not value
            else:
                raise TypeError("Operation 'not' can only be used with flags")
        else:
            raise Exception(f"Invalid operation '{op}'!") #TODO
        ops.pop(0)
    if quotes:
        return repr(value)
    else:
        return value

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
            if type(info.commands[command]) == type(remove_strings): #check if it's a function
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
                        if type(e) == exceptions.ArgumentSyntaxError:
                            raise e
                        raise exceptions.ArgumentSyntaxError(info.scriptname, info.pointer, e)
                    
                    try:
                        #insert here checking the args
                        await command(info, **kwargs)
                    except Exception as e:
                        if type(e) == exceptions.CommandException:
                            raise e
                        raise exceptions.CommandException(info.scriptname, info.pointer, e)
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
    for ch in info.forbidden_characters:
        if ch in label[1:-1]:
            raise exceptions.InvalidNameCharacter(info.scriptname, info.pointer, "label", ch)
    for line in info.script:
        if line.strip().startswith("{" + label + "}"):
            return info.script.index(line)+1
    raise exceptions.UndefinedLabelError(info.scriptname, info.pointer, label)

def compress_labels(info, text): #latter half stolen from remove_strings

    # #get the start and end of every string
    # quotepos = [] #here we'll store the index of every quote that's not been escaped
    # for quote in ("'", "\""):
    #     allpos = [i for i in range(len(text)) if text.startswith(quote, i)] #gets all instances of each type of quotes
    #     for index in allpos:
    #         if text[index-1] != "\\":
    #             quotepos.append(index) #only pass to quotepos the strings that weren't escaped
    # opened_quote = ""
    # quotes = []
    # for index in sorted(quotepos):
    #     if opened_quote == "": #no open quotes
    #         opened_quote = text[index]
    #         quotes.append(index)
    #     elif opened_quote == text[index]:       #current quote is the same as the open quote -> it closes, and
    #         quotes[-1] = (quotes[-1], index)    #otherwise it just gets ignored and treated as any other character
    #         opened_quote = ""

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
    
    #now, replace them with things that won't be screwed up by the rest of input_format
    labels.reverse() #this way the index numbers don't get fucked up
    c = 1
    outlabels = []
    for label in labels:
        outlabels = [text[label[0]+1:label[1]]] + outlabels
        text = text[:label[0]]  + "{" + str(len(labels)-c) + "}" +  text[label[1]+1:] #"0", "1", etc.
        c += 1
    outlabels = [find_label(info, i) for i in outlabels] #gets the positions of the labels
    return text, outlabels

def remove_strings(text): #wow i actually commented this very cool
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
    if opened_quote != "":
        raise SyntaxError(f"AdventureScript syntax: unclosed {opened_quote}")
    #now, replace them with things that won't be screwed up by the rest of input_format
    quotes.reverse() #this way the index numbers don't get fucked up
    c = 1
    quotetext = []
    for quote in quotes:
        quotetext = [text[quote[0]+1:quote[1]]] + quotetext
        text = text[:quote[0]] + f'"{len(quotes)-c}"' + text[quote[1]+1:] #"0", "1", etc.
        c += 1
    outquotes = [i.replace("\\'", "'").replace('\\"', '"') for i in quotetext] #gets all instances of each type of quotes
    return text, outquotes