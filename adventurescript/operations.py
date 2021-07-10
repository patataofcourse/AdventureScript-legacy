from adventurescript.inventory import Inventory
from adventurescript import func

class Operation:
    def __init__(self, name, func, allowed_types = None):
        self.name = name
        self.func = func
        self.allowed_types = allowed_types
    def __call__(self, value, *params):
        type_ = type(value).__name__
        if type_ == "bool": type_ = "flag" 
        if self.allowed_types != None and not type_ in self.allowed_types:
            raise TypeError(f"operation {self.name} can only be used with: {', '.join(self.allowed_types)} (type given was {type_})")
        return self.func(value, *params)

def strOP(value):
    return str(value)
strOP = Operation("str", strOP)

def intOP(value):
    return int(value)
intOP = Operation("int", intOP)

def listOP(value):
    try:
        return list(value)
    except TypeError:
        return [value]
listOP = Operation("list", listOP)

def flag(value):
    if type(value) == str and value.lower() == "false":
        return False
    return bool(value)
flag = Operation("flag", flag)

def item(value, pos):
    return value[int(pos)]
item = Operation("item", item, ["list"])

def ul(value):
    out = ""
    for item in value:
        out += f"•{item}\n"
    return out.strip()
ul = Operation("ul", ul, ["list"])

def ol(value):
    out = ""
    c = 1
    for item in value:
        out += f"{c}- {item}\n"
        c += 1
    return out.strip()
ol = Operation("ol", ol, ["list"])

def money(value):
    return value.money
money = Operation("money", money, ["Inventory"])

def size(value):
    return value.size
size = Operation("size", func, ["Inventory"])

def notOP(value):
    return not value
notOP = Operation("not", notOP, ["flag"])

operations = [strOP, intOP, listOP, flag, item, ul, ol, money, size, notOP]

async def manage_operations(value, ops, quotes=True):
    for op in ops:
        if "(" in op and op.endswith(")"):
            name = op.split("(")[0]
            p = "(".join(op.split("(")[1:])[:-1]
            param = tuple(p.split(","))
        else:
            name = op
            param = ()
        for operation in operations:
            if name == operation.name:
                return operation(value, *param)
                break
    if quotes:
        return repr(value)
    else:
        return value