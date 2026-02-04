from ui import root, sidebar, right_panel
from tkinter import ttk
from tkinterdnd2 import DND_FILES
import tkinter as tk


class OnDropFunc:
    def __init__(self) -> None:
        self.root = lambda paths:None
        self.sidebar = lambda paths:None
        self.right_panel = lambda paths:None
on_drop_function = OnDropFunc()


def _on_drop(event):
    data: str = event.data
    paths = []
    current = []
    in_brace = False
    
    for char in data:
        if char == '{':
            in_brace = True
            current.append(char)
        elif char == '}':
            in_brace = False
            current.append(char)
        elif char == ' ' and not in_brace:
            if current:
                path = ''.join(current).strip('{}')
                if path:
                    paths.append(path)
                current = []
        else:
            current.append(char)
    
    if current:
        path = ''.join(current).strip('{}')
        if path:
            paths.append(path)
    
    on_drop_function.root(paths)


def _on_drop_sidebar(event):
    data: str = event.data
    paths = []
    current = []
    in_brace = False
    
    for char in data:
        if char == '{':
            in_brace = True
            current.append(char)
        elif char == '}':
            in_brace = False
            current.append(char)
        elif char == ' ' and not in_brace:
            if current:
                path = ''.join(current).strip('{}')
                if path:
                    paths.append(path)
                current = []
        else:
            current.append(char)
    
    if current:
        path = ''.join(current).strip('{}')
        if path:
            paths.append(path)
    
    on_drop_function.sidebar(paths)


def _on_drop_right_panel(event):
    data: str = event.data
    paths = []
    current = []
    in_brace = False
    
    for char in data:
        if char == '{':
            in_brace = True
            current.append(char)
        elif char == '}':
            in_brace = False
            current.append(char)
        elif char == ' ' and not in_brace:
            if current:
                path = ''.join(current).strip('{}')
                if path:
                    paths.append(path)
                current = []
        else:
            current.append(char)
    
    if current:
        path = ''.join(current).strip('{}')
        if path:
            paths.append(path)
    
    on_drop_function.right_panel(paths)


root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', _on_drop)

sidebar.drop_target_register(DND_FILES)
sidebar.dnd_bind('<<Drop>>', _on_drop_sidebar)

right_panel.drop_target_register(DND_FILES)
right_panel.dnd_bind('<<Drop>>', _on_drop_right_panel)