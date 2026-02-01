import tkinter as tk
from tkinter import ttk
from ui import root




def ask_choice(title: str, message: str, choices: list[str]) -> str | None:
    """
    弹出自定义选项的询问窗口。
    返回用户选择的字符串，若取消则返回 None。
    """
    top = tk.Toplevel(root)
    top.title(title)
    top.transient(root)
    top.grab_set()
    top.resizable(False, False)
    top.withdraw()

    ttk.Label(top, text=message, padding=12).pack()

    var = tk.StringVar(value=choices[0] if choices else "")
    combo = ttk.Combobox(top, textvariable=var, values=choices, state="readonly", width=30)
    combo.pack(padx=12, pady=6)

    result = None

    def on_ok():
        nonlocal result
        result = var.get()
        top.destroy()

    def on_cancel():
        top.destroy()

    btn_frame = ttk.Frame(top)
    btn_frame.pack(pady=8)
    ttk.Button(btn_frame, text="确定", command=on_ok).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side="left", padx=6)

    top.update_idletasks()
    w = top.winfo_width()
    h = top.winfo_height()
    parent_x = root.winfo_rootx()
    parent_y = root.winfo_rooty()
    parent_w = root.winfo_width()
    parent_h = root.winfo_height()
    x = parent_x + (parent_w - w) // 2
    y = parent_y + (parent_h - h) // 2
    top.geometry(f"+{x}+{y}")
    top.deiconify()

    root.wait_window(top)
    return result







def ask_password(title: str = "输入密码", message: str = "请输入密码：") -> str | None:
    """
    弹出一个密钥输入窗口并等待用户输入，返回输入的密钥。
    若用户取消则返回 None。
    """
    top = tk.Toplevel(root)
    top.title(title)
    top.transient(root)
    top.grab_set()
    top.resizable(False, False)
    top.withdraw()

    ttk.Label(top, text=message, padding=12).pack()

    key_var = tk.StringVar()
    key_entry = tk.Entry(top, textvariable=key_var, show="*", width=30)
    key_entry.pack(padx=12, pady=6)

    result = None

    def on_ok():
        nonlocal result
        result = key_var.get()
        top.destroy()

    def on_cancel():
        top.destroy()

    btn_frame = ttk.Frame(top)
    btn_frame.pack(pady=8)
    ttk.Button(btn_frame, text="确定", command=on_ok).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="取消", command=on_cancel).pack(side="left", padx=6)

    top.bind("<Return>", lambda e: on_ok())

    top.update_idletasks()
    w = top.winfo_width()
    h = top.winfo_height()
    parent_x = root.winfo_rootx()
    parent_y = root.winfo_rooty()
    parent_w = root.winfo_width()
    parent_h = root.winfo_height()
    x = parent_x + (parent_w - w) // 2
    y = parent_y + (parent_h - h) // 2
    top.geometry(f"+{x}+{y}")
    top.deiconify()
    key_entry.focus()

    root.wait_window(top)
    return result