from multithread import threadfunc
from ui.frames.frame_type import FrameType
from ui.waiting import WaitWindow
from encrip import encrip
from ui.notebook import get_current_tab, rename_tab
from tkinter import messagebox, filedialog, BooleanVar
from pathlib import Path



@threadfunc
def save_file_as():
    tab = get_current_tab()
    key = tab.notebook.key_entry.get()
    confirm_key = tab.notebook.confirm_key_entry.get()
    if key != confirm_key:
        messagebox.showwarning("警告",
                               "密钥输入不一致！"
        )
        return

    retain = BooleanVar(value=True)
    match tab.notebook.type:
        case FrameType.TEXT:
            file_path = filedialog.asksaveasfilename(
                title="另存为",
                defaultextension=".enctxt",
                filetypes=[("加密txt文件", "*.enctxt")]
            )
            if file_path:
                ww = WaitWindow("加密中", f'正在加密文本，\n输出路径："{file_path}"', 1)
                def on_close():
                    if messagebox.askyesno("停止加密", "确定停止加密吗？"):
                        retain.set(False)
                ww.set_on_close(on_close)
                try:
                    content: str = tab.notebook.text_editor.get("1.0", "end-1c")
                    encription = encrip(content.encode("utf-8"), key, "")
                    for _ in range(7):
                        if not retain.get(): ww.destroy();return
                        ww.config(current_count=ww.current_count+1/7)
                        next(encription)
                    with open(file_path, "wb") as f:
                        f.write(next(encription))
                    ww.destroy()
                    tab.notebook.path = file_path
                    rename_tab(tab, Path(file_path).name)
                except Exception as e:
                    ww.showerror("错误", f"加密失败，错误信息：{e}")
                    ww.destroy()
                    return
        case FrameType.ENC_ANY:
            dir_path = filedialog.askdirectory(title="另存至")
            if not dir_path: return
            dir_path = Path(dir_path)
            always_cover = False
            count = len(tab.notebook.entry_vars)
            ww = WaitWindow("加密中", "", count)
            def on_close():
                if messagebox.askyesno("停止加密", "确定停止加密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            for path_var, name_var in zip(tab.notebook.entry_vars, tab.notebook.name_vars):
                if not retain.get(): ww.destroy();return
                path = path_var.get()
                name = name_var.get()
                if not name: name = Path(path).stem
                if path:
                    output = dir_path / (name + ".enc" + Path(path).suffix[1:])
                    ww.config(description=f'正在加密{count}个文件，\n当前源路径："{path}"\n当前输出路径："{output}"')
                    if not Path(path).is_file():
                        ww.showerror("错误",f'不存在源文件路径："{path}"\n已跳过此任务')
                        if not retain.get(): ww.destroy();return
                        ww.config(current_count=ww.current_count+1)
                        continue
                    if not name:
                        name = Path(path).stem
                    if output.is_file() and not always_cover:
                        result = ww.showchoice("路径已存在",
                                                f'输出路径："{output}"已存在，您希望：\n\n关闭窗口默认跳过此任务',
                                                ["跳过此任务", "覆盖", "覆盖，本次加密都如此"], retain)
                        if not retain.get(): ww.destroy();return
                        match result:
                            case "跳过此任务"|None:
                                ww.config(current_count=ww.current_count+1)
                                continue
                            case "覆盖":
                                pass
                            case "覆盖，本次加密都如此":
                                always_cover = True
                    with open(path, "rb") as f1:
                        encription = encrip(f1.read(), key, "")
                    for _ in range(7):
                        if not retain.get(): ww.destroy();return
                        ww.config(current_count=ww.current_count+1/7)
                        next(encription)
                    with open(output, "wb") as f2:
                        f2.write(next(encription))
                    ww.config(current_count=ww.current_count+1)
            ww.destroy()
