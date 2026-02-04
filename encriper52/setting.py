import json
import sys
from tkinter import messagebox
from pathlib import Path



debug = True
EXE_PATH = Path(sys.executable if not debug else __file__).parent

class JsonVar:
    _path = ""
    @classmethod
    def _attributes(cls):
        """获取类的所有类属性（不含实例属性）"""
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
    @classmethod
    def dump(cls):
        with open(cls._path, "w", encoding="utf-8") as f:
            json.dump(cls._attributes(), f)
    @classmethod
    def load(cls):
        with open(cls._path, "r", encoding="utf-8") as f:
            attrs = json.load(f)
        for k, v in attrs.items():
            setattr(cls, k, v)


class Setting(JsonVar):
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