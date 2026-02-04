import tkinter as tk
from tkinter import ttk, filedialog
from ui.notebook import remove_tab
from ui.frames.frame_type import FrameType




def build_any_file_frame(parent: tk.Widget) -> None:
    """
    直接在传入的 parent（Frame）上创建支持拖放任意文件的子组件，并布置好所有控件。
    无返回值，所有操作作用于 parent 本身。
    参数:
        parent: 父容器
    """
    parent.configure(style="1.TFrame")

    # 左上角关闭按钮
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    # 绑定关闭事件
    close_btn.config(command=lambda: remove_tab(parent))

    # 提示标签
    tip = tk.Label(parent,
                   text="选择要加密的文件，支持拖拽。",
                   font=(None, 12),
                   fg="#555555",
                   bg="#d9d9d9")
    tip.place(anchor="center", relx=0.5, rely=0.08)

    # 文件列表区域（主体，可滚动）
    list_frame = ttk.Frame(parent)
    list_frame.place(anchor="center", relx=0.5, rely=0.45, relwidth=0.8, relheight=0.6)

    # 内部画布+滚动条，实现动态可编辑输入框列表
    canvas = tk.Canvas(list_frame, bg="#ffffff", highlightthickness=0)
    scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.configure(yscrollcommand=scroll.set)
    
    # 确保 canvas 初始时有最小高度
    canvas.update_idletasks()
    canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), max(100, canvas.winfo_height())))
    
    # 鼠标滚轮滚动事件
    def _on_mouse_wheel(evt):
        # 检查内容是否足够长需要滚动
        bbox = canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            canvas_height = canvas.winfo_height()
            # 只有当内容高度大于 canvas 高度时才允许滚动
            if content_height > canvas_height:
                canvas.yview_scroll(int(-1*(evt.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", _on_mouse_wheel)

    # 内部容器，用于放置输入框
    inner = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner, anchor="nw", width=canvas.winfo_width())

    def _on_inner_configure(_evt=None):
        bbox = canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            canvas_height = canvas.winfo_height()
            # 只有当内容高度大于 canvas 高度时才允许滚动
            if content_height > canvas_height:
                canvas.configure(scrollregion=bbox)
            else:
                # 内容不足时，设置 scrollregion 与 canvas 高度相同，禁用滚动
                canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), canvas_height))
                # 同时重置视图到顶部
                canvas.yview_moveto(0)
        else:
            # 当没有内容时，设置最小滚动区域
            canvas.configure(scrollregion=(0, 0, canvas.winfo_width(), 100))

    def _on_canvas_configure(evt):
        canvas.itemconfigure(canvas.find_all()[0], width=evt.width)

    inner.bind("<Configure>", _on_inner_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    
    # 为 inner 容器本身绑定滚轮事件，处理组件之间的空隙
    inner.bind("<MouseWheel>", _on_mouse_wheel)

    # 存储所有输入框变量
    entry_vars: list[tk.StringVar] = []
    name_vars: list[tk.StringVar] = []

    def _add_file(path: str = "", index: int = -1):
        """添加一个文件项（输入框+命名输入框+选择按钮+移除按钮）"""
        var = tk.StringVar(value=path)
        name_var = tk.StringVar()
        
        # 创建项容器
        item_frame = ttk.Frame(inner)
        item_frame.pack(fill=tk.X, padx=4, pady=2)
        
        # 输入框
        ent = tk.Entry(item_frame, textvariable=var, font=(None, 11))
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ent.bind("<FocusOut>", lambda _e: _refresh_canvas())
        ent.bind("<KeyRelease>", lambda _e: _refresh_canvas())
        
        # 命名提示标签
        name_label = tk.Label(item_frame, text="命名：", font=(None, 9), fg="#888888")
        name_label.pack(side=tk.LEFT, padx=(0, 2))
        
        # 保存名称输入框
        name_ent = tk.Entry(item_frame, textvariable=name_var, font=(None, 11), width=12)
        name_ent.pack(side=tk.LEFT, padx=2)
        name_ent.bind("<FocusOut>", lambda _e: _refresh_canvas())
        name_ent.bind("<KeyRelease>", lambda _e: _refresh_canvas())
        
        # 选择文件按钮
        def _select_for_this():
            file_path = filedialog.askopenfilename()
            if file_path:
                var.set(file_path)
        
        select_btn = ttk.Button(item_frame, text="选择", command=_select_for_this, width=6)
        select_btn.pack(side=tk.LEFT, padx=2)
        
        # 移除按钮
        def _remove_this():
            if len(entry_vars) <= 1:
                return
            item_frame.destroy()
            if var in entry_vars:
                entry_vars.remove(var)
            if name_var in name_vars:
                name_vars.remove(name_var)
            _refresh_canvas()
        
        remove_btn = ttk.Button(item_frame, text="移除", command=_remove_this, width=6)
        remove_btn.pack(side=tk.LEFT, padx=2)
        
        # 为新创建的组件绑定滚轮事件
        item_frame.bind("<MouseWheel>", _on_mouse_wheel)
        ent.bind("<MouseWheel>", _on_mouse_wheel)
        name_label.bind("<MouseWheel>", _on_mouse_wheel)
        name_ent.bind("<MouseWheel>", _on_mouse_wheel)
        select_btn.bind("<MouseWheel>", _on_mouse_wheel)
        remove_btn.bind("<MouseWheel>", _on_mouse_wheel)
        
        # 存储变量
        if index == -1:
            entry_vars.append(var)
            name_vars.append(name_var)
        else:
            entry_vars.insert(index, var)
            name_vars.insert(index, name_var)
        
        return var, name_var

    def _refresh_canvas():
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def add_new_file():
        """添加一个新的空文件项"""
        _add_file()

    # 初始添加一个空输入框
    _add_file()
    
    def add_new_file():
        """添加一个新的空文件项"""
        _add_file()
    
    # 按钮区域 - 只保留添加按钮
    btn_frame = ttk.Frame(parent)
    btn_frame.place(anchor="center", relx=0.5, rely=0.85)
    
    add_btn = ttk.Button(btn_frame, text="添加文件", command=add_new_file)
    add_btn.pack(side=tk.LEFT)
    
    # 密钥输入区域（同一行，与列表框宽度对齐）
    key_frame = ttk.Frame(parent)
    key_frame.place(anchor="center", relx=0.5, rely=0.92, relwidth=0.8)
    
    key_label = tk.Label(key_frame, text="输入密码：", font=(None, 11), fg="#555555", bg="#d9d9d9")
    key_label.pack(side=tk.LEFT, padx=(0, 4))
    
    key_var = tk.StringVar()
    key_entry = tk.Entry(key_frame, textvariable=key_var, font=(None, 11), show="*")
    key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
    
    confirm_key_label = tk.Label(key_frame, text="确认密码：", font=(None, 11), fg="#555555", bg="#d9d9d9")
    confirm_key_label.pack(side=tk.LEFT, padx=(0, 4))
    
    confirm_key_var = tk.StringVar()
    confirm_key_entry = tk.Entry(key_frame, textvariable=confirm_key_var, font=(None, 11), show="*")
    confirm_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    class NoteBook:
        """将容器内所有组件和绑定的变量对象赋值给类属性，方便外部统一访问"""
        def __init__(self):
            # 所有输入框变量
            self.entry_vars = entry_vars
            # 所有保存名称变量
            self.name_vars = name_vars
            # 密钥变量
            self.key_var = key_var
            # 密钥输入框
            self.key_entry = key_entry
            # 确认密钥变量
            self.confirm_key_var = confirm_key_var
            # 确认密钥输入框
            self.confirm_key_entry = confirm_key_entry
            # 提示标签
            self.tip = tip
            # 关闭按钮
            self.close_btn = close_btn
            # 类型
            self.type = FrameType.ENC_ANY
        
        def add_file(self, path: str = ""):
            """添加一个文件项"""
            return _add_file(path)
    
    parent.notebook = NoteBook()
    
    # 为容器绑定滚轮事件
    parent.bind("<MouseWheel>", _on_mouse_wheel)
    
    # 刷新 canvas
    _refresh_canvas()
    
    return parent