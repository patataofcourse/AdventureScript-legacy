class Inventory:
    def __init__(self, size, money=0):
        if size == 0:
            raise Exception("Inventory size cannot be 0") #TODO
        self.inv = [None]*size
        self.size = size
        self.money = money
    def __str__(self):
        return str(self.inv) + ", " + str(self.money)
    def recreate (self, items, money):
        self.inv = items
        self.money = money
    def find(self, item, min_quantity=1):
        for elmt in self.inv:
            if elmt != None and item == elmt[0]:
                return self.inv.index(elmt) if min_quantity <= elmt[1] else None
        return None
    def upgrade(self, plus_size):
        self.inv += [None] * plus_size
        self.size += plus_size
    def downgrade(self, minus_size):
        if len(self.inv) - minus_size <= 0:
            return 0
        elif self.inv.count(None) < minus_size:
            print(self.inv, self.inv.count(None), minus_size)
            return -1 #TODO: add inventory management here
        else:
            self.inv = self.inv[:len(self.inv)-minus_size]
            self.size -= minus_size
            return 1
    def add(self, item, quantity=1):
        item_in_inv = False
        for pair in self.inv:
            if pair != None and item == pair[0]:
                item_in_inv = True
                pos = self.inv.index(pair)
        if item_in_inv:
            self.inv[pos][1] += quantity
            return True
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
        if pos != None:
            self.inv[pos][1] -= quantity
            if self.inv[pos][1] == 0:
                self.inv.pop(pos)
                self.inv.append(None)
            return True
        else:
            return False
    def add_money(self, quantity): #maybe i should add money limit? idfk
        self.money += quantity
        return True
    def remove_money(self, quantity):
        if self.money < quantity:
            return False
        else:
            self.money -= quantity
            return True
    def represent(self):
        out = ""
        for item in self.inv:
            if item == None:
                continue
            out += f"- {item[0]} x{item[1]}\n"
        out = out.strip()
        return out if out != "" else "Empty!"