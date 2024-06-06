from typing import TypeAlias
from utils.instruction import Instruction

Instructions: TypeAlias = list[Instruction]

class Flag:
    def __init__(self, address, name):
        self.address = address
        self.name = name

    def take_instructions(self, passed_instructions: Instructions) -> Instructions:
        taken_instructions = []
        for instruction in passed_instructions:
            if self.address == instruction.address_num:
                taken_instructions.append(instruction)
                break
            taken_instructions.append(instruction)
        return taken_instructions
    
    def is_this_it(self, instruction: Instruction) -> bool:
        return self.address == instruction.address_num