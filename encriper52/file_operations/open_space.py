from tkinter import filedialog, messagebox, BooleanVar
from ui import sidebar, root
from pathlib import Path
from multithread import threadfunc
from ui.ask import ask_password
from encrip import decrip, check
from ui.waiting import WaitWindow
import json
from ui.frames.space import build_space_frame
import ui


def split_header(raw: bytes) -> tuple[bytes, bytes]:
    """从原始字节中分离出头部和剩余内容"""
    if len(raw) < 4:
        raise ValueError("数据太短，无法解析头部长度")
    length = int.from_bytes(raw[:4], 'big')
    header_bytes = raw[4:4+length]
    remaining = raw[4+length:]
    return header_bytes, remaining


def _build_space_on_main_thread(info: dict, space_path: Path, password):
    """在主线程中构建空间界面"""
    for widget in sidebar.winfo_children():
        widget.destroy()
    build_space_frame(sidebar, info, space_path, password)
    
    ui.paned_window.insert(0, sidebar, weight=0)
    window_width = root.winfo_width()
    new_width = int(window_width * 0.4)
    ui.paned_window.sashpos(0, new_width)
    ui.sidebar_ratio = 0.4


def open_space():
    result = filedialog.askdirectory(title="选择秘密空间")
    if result:
        path = Path(result)
        space_file = path / "space"
        
        if not space_file.exists():
            messagebox.showerror("错误", "所选目录不是有效的秘密空间，或秘密空间标识文件被移除")
            return
        
        password = ask_password("输入密码")
        if not password:
            return
        
        space_data = space_file.read_bytes()
        
        @threadfunc(daemon=True)
        def dec_func():
            nonlocal space_data
            retain = BooleanVar(value=True)
            ww = WaitWindow('解密中', f'正在解密秘密空间，\n文件路径："{space_file}"', 1)
            def on_close():
                if messagebox.askyesno("停止解密", "确定停止解密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            
            try:
                decription = decrip(space_data, password)
                for _ in range(7):
                    next(decription)
                    ww.config(current_count=ww.current_count+1/7)
                    if not retain.get():
                        ww.destroy()
                        return
                
                data, header = next(decription)
                info_bytes, decrypted_check = split_header(data)
                
                if decrypted_check != check or header.encode('utf-8') != check:
                    ww.destroy()
                    messagebox.showerror("错误", "密码错误或数据已损坏")
                    return
                
                info = json.loads(info_bytes.decode('utf-8'))
                ww.destroy()
                
                root.after(0, lambda: _build_space_on_main_thread(info, path, password))
                
            except Exception as e:
                ww.destroy()
                messagebox.showerror("错误", f"解密失败：{str(e)}")
                return
        
        dec_func()
