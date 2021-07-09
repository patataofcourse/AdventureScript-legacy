from adventurescript.inventory import Inventory
from adventurescript import func

class Operation:
    def __init__(self, name, func, allowed_types = None):
        self.name = name
        self.func = func
        self.allowed_types = allowed_types
    def execute(self, info, value, *params):
        type_ = type(value).__name__
        if type_ == "bool": type_ = "flag" 
        if not in self.allowed_types:
            raise TypeError(f"operation {self.name} can only be used with: {', '.join(allowed_types)}")
        return self.func(value, *params)

def func(value):
    return str(value)
strOP = Operation("str", func)

def func(value):
    return int(value)
intOP = Operation("int", func)

def func(value):
    try:
        return list(value)
    except TypeError:
        return [value]
listOP = Operation("list", func)

def func(value):
    if type(value) == str and value.lower() == "false":
        return False
    return bool(value)
flag = Operation("flag", func)

def func(value, pos):
    value = value[int(pos)]
elmt = Operation("item", func, ["list"])

def func(value):
    out = ""
    for item in value:
        out += f"•{item}\n"
    value = out.strip()
ul = Operation("ul", func, ["list"])

def func(value)
    out = ""
    c = 1
    for item in value:
        out += f"{c}- {item}\n"
        c += 1
    value = out.strip()
ol = Operation("ol", func, ["list"])

def func(value)
    return value.money
money = Operation("money", func, ["Inventory"])

def func(value)
    return value.size
size = Operation("size", func, ["Inventory"])

def func(value)
    return not value
notOP = Operation("not", func, ["flag"])

operations = [strOP, intOP, listOP, flag, elmt, ul, ol, money, size, notOP]

async def manage_operations(value, ops, quotes=True):
    for op in ops:
        if "(" in op and op.endswith(")"):
            name = op.split("(")[0]
            #TODO: get param
        #TODO: for operation in operations, if op == operation.name, execute operation
    if quotes:
        return repr(value)
    else:
        return value