import ctypes
from utils.instruction import Instruction

def get_emulation(input, architecture):
    shellcode = bytes.fromhex(input)
    buff = ctypes.create_string_buffer(shellcode, len(shellcode))
    handle = ctypes.WinDLL(r".\BddisasmIntegration\x64\Debug\BddisasmIntegration.dll")
    shemuStatus = ctypes.c_uint32(0)
    shemuStatusPtr = ctypes.pointer(shemuStatus)
    flags = ctypes.c_uint64(0)
    flagsPtr = ctypes.pointer(flags)
    result = ctypes.c_int32(0)    
    bufsize = 100000
    emuRes = ctypes.create_string_buffer(bufsize)
    handle.ExpAnalyzeShellcode.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64), ctypes.c_char_p, ctypes.c_uint64]
    handle.ExpAnalyzeShellcode.restype = ctypes.c_int32
    result = handle.ExpAnalyzeShellcode(buff, len(shellcode), architecture == 'x86', shemuStatusPtr, flagsPtr, emuRes, bufsize)
    return emuRes.value.decode()

def get_disasm(input, architecture):
    shellcode = bytes.fromhex(input)
    buff = ctypes.create_string_buffer(shellcode, len(shellcode))
    handle = ctypes.WinDLL(r".\BddisasmIntegration\x64\Debug\BddisasmIntegration.dll")

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