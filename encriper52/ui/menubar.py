import tkinter as tk
from typing import Callable

def parse_accelerator(accelerator: str) -> str:
    parts = accelerator.split('+')
    modifiers = []
    key = ''
    
    modifier_map = {
        'CTRL': 'Control',
        'ALT': 'Alt',
        'SHIFT': 'Shift',
        'CMD': 'Command',
        'META': 'Meta'
    }
    
    for part in parts:
        part_upper = part.upper()
        if part_upper in modifier_map:
            modifiers.append(modifier_map[part_upper])
        else:
            key = part
    
    if modifiers:
        if 'Shift' in modifiers:
            key = key.upper()
        else:
            key = key.lower()
        return '<' + '-'.join(modifiers) + '-' + key + '>'
    else:
        return key

def menubar(master: tk.Tk|tk.Toplevel, structure: dict[str,dict|Callable]):
    mb = tk.Menu(master)
    for k1, v1 in structure.items():
        if type(v1) == dict:
            menu = tk.Menu(mb, tearoff=0)
            for k2, v2 in v1.items():
                if v2:
                    if type(v2) == tuple:
                        menu.add_command(label=k2, command=v2[0], accelerator=v2[1])
                        key = parse_accelerator(v2[1])
                        master.bind(key, lambda e, cmd=v2[0]: cmd())
                    else:
                        menu.add_command(label=k2, command=v2)
                else:
                    menu.add_separator()
            mb.add_cascade(label=k1, menu=menu)
        else:
            mb.add_command(label=k1, command=v1)
    master.config(menu=mb)