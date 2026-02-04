import tkinter as tk
from tkinter import ttk
from ui.frames.frame_type import FrameType
from ui.notebook import remove_tab


def build_welcom_frame(parent: tk.Widget) -> None:
    """
    在传入的 parent 容器上布置"欢迎界面"。
    不创建新对象，直接作用于 parent。
    """
    label = tk.Label(parent,
             text="点击文件>新建秘密空间，或用Alt+N可新建\n点击文件>打开秘密空间，或用Alt+O可打开\n\n使用前务必查看帮助>使用须知",
             font=(None, 12),
             wraplength=400,
             justify="center")
    label.pack(expand=True, fill="both", padx=20, pady=20)
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    close_btn.config(command=lambda: remove_tab(parent))
    
    def update_wraplength(event=None):
        try:
            label.configure(wraplength=max(100, parent.winfo_width() - 40))
        except:
            pass
    
    parent.bind("<Configure>", update_wraplength)
    update_wraplength()

    class NoteBook:
        def __init__(self) -> None:
            self.type = FrameType.WELCOME
    
    parent.notebook = NoteBook()