from tkinter import messagebox
from pathlib import Path
import tempfile
import webbrowser


import setting
from ui import root
from ui.menubar import menubar
from ui.notebook import get_current_tab, add_tab, tabs_dict, switch_to_tab
from ui.frames.welcome import build_welcom_frame
from ui.dropevent import on_drop_function
from ui.frames.frame_type import FrameType
from file_operations import new_file, new_space, open_file, open_space, save_file, save_file_as, save_in_space





build_welcom_frame(add_tab('<欢迎界面>'))


def on_drop(paths: list[str]):
    tab = get_current_tab()
    if tab.notebook.type == FrameType.ENC_ANY:
        existing_paths = [var.get() for var in tab.notebook.entry_vars]
        
        if len(existing_paths) == 1 and not existing_paths[0]:
            tab.notebook.entry_vars[0].set(paths[0])
            for path in paths[1:]:
                if path not in existing_paths:
                    tab.notebook.add_file(path)
        else:
            for path in paths:
                if path not in existing_paths:
                    tab.notebook.add_file(path)
on_drop_function.right_panel = on_drop


def welcome():
    if not '<欢迎界面>' in tabs_dict.values():
        f = add_tab('<欢迎界面>')
        build_welcom_frame(f)
        switch_to_tab(f)
def close_space():
    try:
        import ui
        ui.paned_window.forget(ui.sidebar)
        for widget in ui.sidebar.winfo_children():
            widget.destroy()
    except Exception:
        pass


def setting():
    pass

def should_know():
    pass
def show_temp_path():
    temp_dir = tempfile.gettempdir()
    try:
        temp_path = Path(temp_dir)
        if not temp_path.is_dir():
            raise Exception('路径不存在或目标非文件夹')
        webbrowser.open(temp_path.as_uri())
    except Exception as e:
        messagebox.showerror("错误", f"无法打开临时文件目录: {e}\n\n临时文件路径: {temp_dir}")


menubar(root,
{
"文件":{"新建加密文件":(new_file, "Ctrl+N"),
        "新建秘密空间":(new_space, "Alt+N"),
        "1":None,
        "打开加密文件":(open_file, "Ctrl+O"),
        "打开秘密空间":(open_space, "Alt+O"),
        "2":None,
        "保存":(save_file, "Ctrl+S"),
        "另存为":(save_file_as, "Ctrl+Shift+S"),
        "存入空间":(save_in_space, "Alt+S")},
"视图":{"欢迎界面":welcome,
        "关闭秘密空间":close_space},
"设置":setting,
"帮助":{"使用须知":should_know,
        "临时文件路径":show_temp_path}
}
)



if __name__ == "__main__":
    root.mainloop()