from ui.ask import ask_choice
from ui.notebook import add_tab, switch_to_tab
from ui.frames.text_frame import build_text_frame
from ui.frames.any_file_frame import build_any_file_frame


def text_frame(name, path=None):
    frame = add_tab(name)
    build_text_frame(frame)
    switch_to_tab(frame)
    frame.notebook.path = path
    return frame


def any_frame(name, path=None):
    if path is None:
        frame = add_tab(name)
        build_any_file_frame(frame)
        switch_to_tab(frame)
        frame.notebook.path = path
        return frame
    else:
        pass


def new_file():
    result = ask_choice("新建文件",
               "以何种方式新建加密文件？",
               ["选择原始文件", "编辑文本"])
    if result:
        if result == "编辑文本":
            text_frame("<编辑文本>")
        elif result == "选择原始文件":
            any_frame("<选择文件>")
