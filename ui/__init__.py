from tkinter import ttk
import tkinter as tk
from tkinterdnd2 import TkinterDnD



root = TkinterDnD.Tk()
root.title("文件锁")
# 获取屏幕宽高
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# 设置窗口大小
window_width = 800
window_height = 600
# 计算居中坐标
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
# 设置窗口大小并置中
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
# 设置窗口最小尺寸
root.minsize(window_width, window_height)



# 创建左右分栏的 PanedWindow
paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 创建左侧侧栏容器
sidebar = ttk.Frame(paned_window, width=200)
paned_window.add(sidebar, weight=0)

# 创建右侧容器（用于放置 Notebook）
right_panel = ttk.Frame(paned_window)
paned_window.add(right_panel, weight=1)

# 保存侧栏相对比例
sidebar_ratio = 0.25
last_window_width = window_width


def update_sidebar_width():
    global sidebar_ratio, last_window_width
    current_window_width = root.winfo_width()
    if current_window_width != last_window_width:
        last_window_width = current_window_width
        new_width = int(current_window_width * sidebar_ratio)
        min_width = current_window_width // 5
        max_width = current_window_width // 2
        
        if new_width < min_width:
            new_width = min_width
            sidebar_ratio = min_width / current_window_width
        elif new_width > max_width:
            new_width = max_width
            sidebar_ratio = max_width / current_window_width
        
        paned_window.sashpos(0, new_width)


def on_window_configure(event):
    if event.widget == root:
        update_sidebar_width()


def on_sash_drag(event):
    global sidebar_ratio
    window_width = root.winfo_width()
    min_width = window_width // 5
    max_width = window_width // 2
    
    if event.x < min_width:
        paned_window.sashpos(0, min_width)
        sidebar_ratio = min_width / window_width
    elif event.x > max_width:
        paned_window.sashpos(0, max_width)
        sidebar_ratio = max_width / window_width
    else:
        paned_window.sashpos(0, event.x)
        sidebar_ratio = event.x / window_width


root.bind('<Configure>', on_window_configure)
paned_window.bind('<ButtonRelease-1>', on_sash_drag)




style = ttk.Style()
# 创建一个凹陷、亮灰色样式
style.configure("1.TFrame",
                background="#d9d9d9",          # 亮灰色背景
                relief="sunken",                # 凹陷边框
                borderwidth=2)                # 边框宽度

# 配置Notebook标签样式，增大标签大小
style.configure("TNotebook.Tab",
                padding=[7, 2])              # 标签内边距 [左右, 上下]