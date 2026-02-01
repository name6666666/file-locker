import tkinter as tk
from ui.frames.frame_type import FrameType



def build_no_space_frame(parent: tk.Widget) -> None:
    """
    在传入的 parent 容器上布置“未打开秘密空间”提示界面。
    不创建新对象，直接作用于 parent。
    """
    parent.configure(style="1.TFrame")
    tk.Label(parent,
             text="未打开秘密空间。\n点击文件>新建秘密空间，或用Alt+N可新建；\n点击文件>打开秘密空间，或用Alt+O可打开。",
             font=(None, 12),
             bg="#d9d9d9").place(anchor="center", relx=0.5, rely=0.5)

    class NoteBook:
        def __init__(self) -> None:
            self.type = FrameType.NO_SPACE
    
    parent.notebook = NoteBook()