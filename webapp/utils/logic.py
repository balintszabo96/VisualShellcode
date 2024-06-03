import ctypes
from utils.instruction import Instruction

def get_disasm(input, architecture):
    shellcode = bytes.fromhex(input)
    buff = ctypes.create_string_buffer(shellcode, len(shellcode))
    handle = ctypes.WinDLL(r".\BddisasmIntegration\x64\Release\BddisasmIntegration.dll")

    #result = ctypes.c_int32(0)
    bufsize = 100000
    disasm = ctypes.create_string_buffer(bufsize)
    handle.ExpDisasmShellcode.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_char_p, ctypes.c_uint64]
    handle.ExpDisasmShellcode.restype = ctypes.c_int32
    handle.ExpDisasmShellcode(buff, len(shellcode), architecture == 'x86', disasm, bufsize)
    
    disasm_lines = disasm.value.decode().split('\n')[:-1]
    instructions = []
    for line in disasm_lines:
        trimmed = ' '.join(line.split())
        line_split = trimmed.split(' ')
        address = line_split[0]
        opcodes = line_split[1]
        operation = line_split[2]
        text = ' '.join(line_split[3:])
        instructions.append(Instruction(address, opcodes, operation, text))
    return instructions