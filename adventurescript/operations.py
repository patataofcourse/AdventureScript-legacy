from adventurescript.inventory import Inventory
class Operation:
    def __init__(self, name, func, allowed_types = None):
        self.name = name
        self.func = func
        self.allowed_types = allowed_types
    def execute(self, value):
        return self.func(value)

operations = [strOP, intOP, listOP, flag, elmt, ul, ol, money, size, notOP]

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