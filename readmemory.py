from ctypes import *
from ctypes.wintypes import *
from time import sleep
import win32process, win32gui, psutil

PROCESS_ID = 3340
PROCESS_VM_READ = 0x0010
STRLEN = 255
PROCESS_HEADER_ADDR = 0x70E000

k32 = WinDLL('kernel32')
k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
k32.OpenProcess.restype = HANDLE
k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
k32.ReadProcessMemory.restype = BOOL

process = k32.OpenProcess(PROCESS_VM_READ, 0, PROCESS_ID)


while True:
    buf = create_string_buffer(STRLEN)
    s = c_size_t()

    print ('process: ' + str(process))
    print ('buf: ' + str(buf))
    print ('s: ' + str(s))

    if k32.ReadProcessMemory(process, PROCESS_HEADER_ADDR, buf, STRLEN, byref(s)):
        print(s.value,buf.raw)

    sleep(1)