import ctypes

def get_disasm(input, architecture):
    shellcode = bytes.fromhex(input)
    buff = ctypes.create_string_buffer(shellcode, len(shellcode))
    handle = ctypes.WinDLL(r".\BddisasmIntegration\x64\Release\BddisasmIntegration.dll")

    result = ctypes.c_int32(0)
    bufsize = 100000
    disasm = ctypes.create_string_buffer(bufsize)
    handle.ExpDisasmShellcode.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.c_char_p, ctypes.c_uint64]
    handle.ExpDisasmShellcode.restype = ctypes.c_int32
    result = handle.ExpDisasmShellcode(buff, len(shellcode), architecture == 'x86', disasm, bufsize)
    return disasm.value.decode()