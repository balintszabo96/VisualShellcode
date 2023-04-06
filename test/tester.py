import ctypes

handle = ctypes.WinDLL(r"b:\projects\VisualShellcode\BddisasmIntegration\x64\Release\BddisasmIntegration.dll")
print(handle.Dummy)
buff = ctypes.create_string_buffer(b"Hello", 10)
handle.Dummy.argtypes = [ctypes.c_char_p]
handle.Dummy(buff)