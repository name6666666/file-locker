import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import askstring as ask_choice
from ui import right_panel




# 在 right_panel 容器中创建标签栏（Notebook）
tab_notebook = ttk.Notebook(right_panel)
tab_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 全局字典：保存所有已创建的标签页 {Frame: 标签名}
tabs_dict: dict[ttk.Frame, str] = {}

def _get_base_name(name: str) -> str:
    """
    获取基础名称（移除开头的 * 标记）。
    """
    return name[1:] if name.startswith("*") else name

def _generate_unique_name(base_name: str) -> str:
    """
    生成唯一的标签页名称。
    如果 base_name 已存在（忽略开头的 *），则添加 <1>, <2> 等标号。
    """
    # 获取所有标签页的基础名称（移除开头的 *）
    existing_base_names = [_get_base_name(name) for name in tabs_dict.values()]
    
    if base_name not in existing_base_names:
        return base_name
    
    counter = 1
    while True:
        new_name = f"{base_name}<{counter}>"
        if new_name not in existing_base_names:
            return new_name
        counter += 1

def add_tab(tab_name: str) -> ttk.Frame:
    """
    新建一个标签页，返回对应的 Frame 容器。
    若名称已存在（忽略开头的 *）则自动添加标号区分。
    参数:
        tab_name: 标签页名称
    """
    # 生成唯一名称（会自动处理重名情况，忽略开头的 *）
    unique_name = _generate_unique_name(tab_name)
    frame = ttk.Frame(tab_notebook)
    tab_notebook.add(frame, text=unique_name)
    tabs_dict[frame] = unique_name
    return frame

def remove_tab(frame: ttk.Frame) -> bool:
    """
    关闭并销毁指定 Frame 对应的标签页。
    成功返回 True，若 Frame 不存在返回 False。
    """
    if frame not in tabs_dict:
        return False
    del tabs_dict[frame]
    tab_notebook.forget(frame)
    frame.destroy()
    return True

def switch_to_tab(frame: ttk.Frame) -> bool:
    """
    切换到指定 Frame 对应的标签页。
    成功返回 True，若 Frame 不存在返回 False。
    """
    if frame not in tabs_dict:
        return False
    tab_notebook.select(frame)
    return True

def get_current_tab() -> ttk.Frame | None:
    """
    获取当前选中的标签页，仅返回容器对象（Frame）。
    若没有任何标签页返回 None。
    """
    current = tab_notebook.select()
    if not current:
        return None
    # 从字典中直接查找
    for frame in tabs_dict:
        if str(frame) == current:
            return frame
    return None

def get_user_tab_choice() -> ttk.Frame | None:
    """
    弹出一个简单对话框，列出当前所有标签页供用户选择。
    返回用户选中的标签页 Frame；若取消则返回 None。
    """
    if not tabs_dict:
        return None
    names = list(tabs_dict.values())
    chosen_name = ask_choice("选择标签页", "请选择要切换到的标签页：", names)
    if chosen_name is None:
        return None
    # 根据名称反查 Frame
    for frame, name in tabs_dict.items():
        if name == chosen_name:
            return frame
    return None

def rename_tab(frame: ttk.Frame, new_name: str) -> bool:
    """
    重命名指定 Frame 对应的标签页。
    若名称已存在（忽略开头的 *）则自动添加标号区分。
    成功返回 True，若 Frame 不存在或新名称为空返回 False。
    """
    if frame not in tabs_dict or not new_name.strip():
        return False
    # 生成唯一名称（会自动处理重名情况，忽略开头的 *）
    unique_name = _generate_unique_name(new_name)
    # 更新字典与标签显示文本
    tabs_dict[frame] = unique_name
    tab_notebook.tab(frame, text=unique_name)
    return True

def mark_tab_modified(frame: ttk.Frame, modified: bool = True) -> bool:
    """
    标记或取消标记标签页为已修改状态（在名称前添加 *）。
    成功返回 True，若 Frame 不存在返回 False。
    """
    if frame not in tabs_dict:
        return False
    current_name = tabs_dict[frame]
    if modified:
        if not current_name.startswith("*"):
            tabs_dict[frame] = "*" + current_name
            tab_notebook.tab(frame, text=tabs_dict[frame])
    else:
        if current_name.startswith("*"):
            tabs_dict[frame] = current_name[1:]
            tab_notebook.tab(frame, text=tabs_dict[frame])
    return True