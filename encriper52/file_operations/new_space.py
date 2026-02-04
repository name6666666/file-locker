from tkinter import filedialog, messagebox, BooleanVar
from pathlib import Path
from multithread import threadfunc
from ui.ask import ask_password
from encrip import encrip, check
import json
from datetime import datetime
from ui.waiting import WaitWindow



def add_header(header_bytes: bytes, raw_bytes: bytes) -> bytes:
    """给字节添加头部，格式为：4字节长度 + 头部内容 + 原字节"""
    length = len(header_bytes)
    return length.to_bytes(4, 'big') + header_bytes + raw_bytes


def new_space():
    result = filedialog.askdirectory(title="选择路径")
    if result:
        dirname = ask_password("输入命名", "输入秘密空间名称：", False)
        if not dirname: return

        path = Path(result)
        space_path = path / dirname
        try:
            space_path.mkdir()
        except Exception:
            messagebox.showerror("错误", 
                                 "文件夹已存在或不合规的字符")
        space_path.rmdir()
        
        password = ask_password("设置密码")
        confirm = ask_password("确认密码", "再次输入密码：")
        if confirm != password:
            messagebox.showwarning("警告",
                                   "密码不一致！")
            return

        space_path.mkdir()
        info = json.dumps({'name':dirname, 'date':datetime.now().isoformat()})
        space_file = add_header(info.encode('utf-8'), check)
        encription = encrip(space_file, password, check.decode('utf-8'))
        @threadfunc(daemon=True)
        def enc_func():
            nonlocal space_file
            retain = BooleanVar(value=True)
            ww = WaitWindow('创建中', f'正在创建秘密空间标识文件，\n文件路径："{space_path / "space"}"', 1)
            def on_close():
                if messagebox.askyesno("停止加密", "确定停止加密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            for _ in range(7):
                next(encription)
                ww.config(current_count=ww.current_count+1/7)
                if not retain.get(): 
                    ww.destroy()
                    return
            space_file = next(encription)
            (space_path / "space").write_bytes(space_file)
            ww.destroy()
        enc_func()
