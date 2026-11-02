import ctypes, ctypes.util

libc = ctypes.CDLL(ctypes.util.find_library("c"))
libc.getpid.restype = ctypes.c_int
print("agent v0 (python), pid=", libc.getpid())
input("Press Enter to exit")
