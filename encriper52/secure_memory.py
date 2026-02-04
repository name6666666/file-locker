import ctypes
import sys
from typing import Optional, Union


class SecureBytes:
    def __init__(self, data: Union[bytes, bytearray, str]):
        if isinstance(data, str):
            self._data = bytearray(data.encode())
        elif isinstance(data, bytearray):
            self._data = data
        else:
            self._data = bytearray(data)
        
        if len(self._data) > 0:
            self._lock_memory()
    
    def _lock_memory(self):
        try:
            if sys.platform == 'win32':
                ctypes.windll.kernel32.VirtualLock(
                    ctypes.addressof(self._data),
                    len(self._data)
                )
        except:
            pass
    
    def _unlock_memory(self):
        try:
            if sys.platform == 'win32' and hasattr(self, '_data'):
                ctypes.windll.kernel32.VirtualUnlock(
                    ctypes.addressof(self._data),
                    len(self._data)
                )
        except:
            pass
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __bytes__(self):
        return bytes(self._data)
    
    def __str__(self):
        return bytes(self._data).decode('utf-8')
    
    def __eq__(self, other):
        if isinstance(other, SecureBytes):
            return bytes(self) == bytes(other)
        elif isinstance(other, (bytes, bytearray)):
            return bytes(self) == bytes(other)
        elif isinstance(other, str):
            return str(self) == other
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def wipe(self):
        if hasattr(self, '_data'):
            self._unlock_memory()
            for i in range(len(self._data)):
                self._data[i] = 0
    
    def __del__(self):
        self.wipe()


def secure_wipe(data: bytearray):
    for i in range(len(data)):
        data[i] = 0


def lock_memory(data: bytearray) -> bool:
    try:
        if sys.platform == 'win32' and len(data) > 0:
            ctypes.windll.kernel32.VirtualLock(
                ctypes.addressof(data),
                len(data)
            )
        return True
    except:
        return False


def unlock_memory(data: bytearray) -> bool:
    try:
        if sys.platform == 'win32' and len(data) > 0:
            ctypes.windll.kernel32.VirtualUnlock(
                ctypes.addressof(data),
                len(data)
            )
        return True
    except:
        return False
