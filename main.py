from tkinter import messagebox
import sys
from pathlib import Path


import jsonvar
from ui import root, sidebar
from ui.menubar import menubar
from ui.notebook import add_tab, get_current_tab
from ui.frames.no_space import build_no_space_frame
from ui.dropevent import on_drop_function
from ui.frames.frame_type import FrameType
from file_operations import new_file, new_space, open_file, open_space, save_file, save_file_as, save_in_space




debug = True
EXE_PATH = Path(sys.executable if not debug else __file__).parent


class Setting(jsonvar.JsonVar):
    _path = EXE_PATH / "setting.json"
    recent_secret_space = ""

if (EXE_PATH / "setting.json").is_file():
    try:
        Setting.load()
    except:
        if messagebox.askyesno("配置文件出错",
                               "存储设置信息的配置文件无法解析，您希望覆写为初始配置文件吗？"):
            Setting.dump()
        else:
            sys.exit(1)
else:
    Setting.dump()




build_no_space_frame(add_tab("<未打开秘密空间>"))


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


def setting():
    pass

def help_item():
    pass


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
"设置":setting,
"帮助":help_item
}
)




root.mainloop()