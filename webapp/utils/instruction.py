class Flag:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def get_id(self):
        return str(self.id)
    
    def get_name(self):
        return self.name
        

class Instruction:
    def __init__(self, address, opcodes, operation, text):
        self.address = address
        self.address_num = int(address, 16)
        self.opcodes = opcodes
        self.operation = operation
        self.text = text
        self.flags = []
    
    def has_flags(self) -> bool:
        return len(self.flags) > 0

    def get_flags(self) -> str:
        return ','.join(self.flags)

    def __str__(self) -> str:
        return f"{self.address}\t\t\t\t{self.opcodes}\t\t\t\t{self.text}"