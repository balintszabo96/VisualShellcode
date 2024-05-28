import ctypes
import os

handle = ctypes.WinDLL(r".\BddisasmIntegration\x64\Release\BddisasmIntegration.dll")
with open(r"e:\ex\projects\VisualShellcode\test\shellcodes\exec_calc_x64", 'rb') as f:
    shellcode = f.read()
buff = ctypes.create_string_buffer(shellcode, len(shellcode))
shemuStatus = ctypes.c_uint32(0)
shemuStatusPtr = ctypes.pointer(shemuStatus)
flags = ctypes.c_uint64(0)
flagsPtr = ctypes.pointer(flags)
result = ctypes.c_int32(0)
handle.ExpAnalyzeShellcode.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_bool, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64)]
handle.ExpAnalyzeShellcode.restype = ctypes.c_int32
result = handle.ExpAnalyzeShellcode(buff, len(shellcode), False, shemuStatusPtr, flagsPtr)
print("here")