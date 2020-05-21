from adventurescript import commands, exceptions

# This function takes a string and does a sort of eval() with it, but using AS' variables, flags and lists;
# and also counts the #.# expressions using AS' own values (so, #.int, for example).
async def input_format(info, text):
    # Warning: badly named variables ahead
    text = text.split("+")  # text2 is used as a way to store the text through the loop, so like a temp variable
    text2 = text + []
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
                if (subsubitem.startswith("'") and subsubitem.endswith("'")) or (subsubitem.startswith('"') and subsubitem.endswith('"')):
                    value = subsubitem
                    ops = []
                else:
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
    return eval(text2)

async def manage_operations(value, ops):
    for op in ops:
        if op == "str":
            value = str(value)
        elif op == "int":
            value = int(value)
        elif op == "list":
            try:
                value = list(value)
            except TypeError:
                value = [value]
        elif op == "flag":
            if value.lower == "false":
                value = False
            value = bool(value)
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
        else:
            raise Exception(f"Invalid operation '{op}'!") #TODO
        ops.pop(0)
    return str_but_quotes(value)             

def str_but_quotes(value):
    if type(value) == type(""):
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
        for command in commands.commands:
            if command.__name__ == line[0]:
                kwargs = {}
                if line[1] == "":
                    await command(info)
                    return True
                for pair in line[1:]:
                    pair = pair.split("=")
                    kwargs[pair[0].strip()] = await input_format(info,pair[1])
                await command(info, **kwargs)
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
        if line.strip().find(label) == 0:
            return info.script.index(line)+1
    raise Exception(f"Label '{label}' not found!")