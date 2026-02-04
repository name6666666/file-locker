import tkinter as tk
from tkinter import ttk
from pathlib import Path
from ui.frames.frame_type import FrameType
from secure_memory import SecureBytes


FILE_TYPE_ALL = "全部"
FILE_TYPE_TEXT = "文本"
FILE_TYPE_AUDIO = "音频"
FILE_TYPE_VIDEO = "视频"
FILE_TYPE_IMAGE = "图片"
FILE_TYPE_OTHER = "其他"

FILE_TYPES = [FILE_TYPE_ALL, FILE_TYPE_TEXT, FILE_TYPE_AUDIO, FILE_TYPE_VIDEO, FILE_TYPE_IMAGE, FILE_TYPE_OTHER]


def build_space_frame(parent: tk.Widget, space_info: dict = None, space_path: Path = None, space_password: str = None) -> None:
    """
    在传入的 parent 容器上布置秘密空间文件列表界面。
    不创建新对象，直接作用于 parent。
    """
    parent.configure(style="1.TFrame")
    
    main_container = tk.Frame(parent, bg="#d9d9d9")
    main_container.pack(fill="both", expand=True)
    
    left_panel = tk.Frame(main_container, bg="#e0e0e0", width=120)
    left_panel.pack(side="left", fill="y", padx=(5, 2), pady=5)
    
    close_btn = tk.Button(left_panel, text="✕", font=(None, 12), 
                        bg="#e0e0e0", fg="#666666", 
                        activebackground="#d0d0d0", activeforeground="#333333",
                        relief="flat", borderwidth=0,
                        padx=5, pady=2)
    close_btn.pack(anchor="w", pady=(0, 10))
    
    def close_space():
        import ui
        ui.paned_window.forget(ui.sidebar)
    
    close_btn.config(command=close_space)
    
    right_panel = tk.Frame(main_container, bg="#d9d9d9")
    right_panel.pack(side="left", fill="both", expand=True, padx=(2, 5), pady=5)
    
    if space_info:
        info_frame = tk.Frame(right_panel, bg="#d9d9d9", relief="ridge", borderwidth=1)
        info_frame.pack(fill="x", pady=(0, 10))
        
        name_label = tk.Label(info_frame, text=f"空间名称: {space_info.get('name', '未知')}", 
                             font=(None, 10, "bold"), bg="#d9d9d9", fg="#333333", anchor="w")
        name_label.pack(fill="x", padx=5, pady=(5, 2))
        
        date_str = space_info.get('date', '')
        if date_str:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(date_str)
                date_label = tk.Label(info_frame, text=f"创建日期: {dt.strftime('%Y-%m-%d %H:%M')}", 
                                     font=(None, 9), bg="#d9d9d9", fg="#666666", anchor="w")
                date_label.pack(fill="x", padx=5, pady=(0, 5))
            except:
                pass
    
    selected_type = tk.StringVar(value=FILE_TYPE_ALL)
    
    def on_type_selected(event=None):
        pass
    
    for file_type in FILE_TYPES:
        rb = tk.Radiobutton(
            left_panel,
            text=file_type,
            variable=selected_type,
            value=file_type,
            command=on_type_selected,
            bg="#e0e0e0",
            fg="#333333",
            selectcolor="#b8d4e8",
            activebackground="#e0e0e0",
            activeforeground="#333333",
            indicatoron=0,
            anchor="w",
            padx=10,
            pady=5
        )
        rb.pack(anchor="w", pady=2)
    
    search_frame = tk.Frame(right_panel, bg="#d9d9d9")
    search_frame.pack(fill="x", pady=(0, 5))
    
    search_label = tk.Label(search_frame, text="搜索:", bg="#d9d9d9", fg="#333333")
    search_label.pack(side="left", padx=(0, 5))
    
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side="left", fill="x", expand=True)
    
    list_frame = tk.Frame(right_panel, bg="#ffffff")
    list_frame.pack(fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    
    file_list = tk.Listbox(
        list_frame,
        yscrollcommand=scrollbar.set,
        bg="#ffffff",
        fg="#333333",
        selectbackground="#b8d4e8",
        selectforeground="#ffffff",
        font=(None, 9),
        borderwidth=0,
        highlightthickness=0
    )
    file_list.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=file_list.yview)
    
    class NoteBook:
        def __init__(self) -> None:
            self.type = FrameType.SPACE
            self.selected_type = selected_type
            self.search_entry = search_entry
            self.file_list = file_list
            self.on_type_selected = on_type_selected
            self.path = space_path
            self.password = SecureBytes(space_password) if space_password else None
        
        def __del__(self):
            if hasattr(self, 'password') and self.password:
                self.password.wipe()
    
    parent.notebook = NoteBook()
