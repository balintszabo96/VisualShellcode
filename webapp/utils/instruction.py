class Instruction:
    def __init__(self, address, opcodes, operation, text):
        self.address = address
        self.address_num = int(address, 16)
        self.opcodes = opcodes
        self.operation = operation
        self.text = text