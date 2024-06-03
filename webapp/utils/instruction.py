class Instruction:
    def __init__(self, address, opcodes, operation, text):
        self.address = address
        self.opcodes = opcodes
        self.operation = operation
        self.text = text
    
    def __str__(self) -> str:
        return f"{self.address}\t\t\t\t{self.opcodes}\t\t\t\t{self.text}"