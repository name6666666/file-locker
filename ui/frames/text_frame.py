import tkinter as tk
from tkinter import ttk
from ui.notebook import remove_tab, mark_tab_modified
from ui.frames.frame_type import FrameType



def build_text_frame(parent: tk.Widget) -> None:
    """
    直接在传入的 parent（Frame）上创建带文本编辑器的子组件，并分为上下两个区域。
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

    # 根据按钮高度调整顶部距离
    top_distance = 34

    # 上方：文本编辑器区域
    editor_frame = ttk.Frame(parent)
    editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(top_distance, 0))

    # 添加滚动条
    text_scroll = ttk.Scrollbar(editor_frame)
    text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # 创建文本编辑器
    text_editor = tk.Text(editor_frame,
                          wrap=tk.WORD,
                          yscrollcommand=text_scroll.set,
                          undo=True,
                          font=(None, 12))
    text_editor.pack(fill=tk.BOTH, expand=True)
    # 配置滚动条
    text_scroll.config(command=text_editor.yview)
    # 绑定文本编辑器内容改变事件
    def on_text_change(event=None):
        if not parent.notebook.setting_value:
            # 检查 Text 组件是否真的被修改了
            if text_editor.edit_modified():
                mark_tab_modified(parent, True)
                # 重置 modified 标志，防止重复触发
                text_editor.edit_modified(False)
    text_editor.bind("<<Modified>>", on_text_change)
    text_editor.bind("<KeyRelease>", on_text_change)

    # 下方：密钥输入区域
    key_frame = ttk.Frame(parent)
    key_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    # 密钥输入提示标签
    key_label = tk.Label(key_frame,
                         text="输入密码：",
                         font=(None, 12),
                         fg="#555555",
                         bg="#d9d9d9")
    key_label.pack(side=tk.LEFT, padx=(0, 8))
    # 密钥输入框（显示星号）
    key_var = tk.StringVar()
    key_entry = tk.Entry(key_frame,
                         textvariable=key_var,
                         font=(None, 11),
                         fg="#000000",
                         bg="#ffffff",
                         relief="groove",
                         bd=2,
                         show="*")
    key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    # 绑定密码输入框内容改变事件
    def on_key_change(event=None):
        if not parent.notebook.setting_value:
            mark_tab_modified(parent, True)
    key_entry.bind("<KeyRelease>", on_key_change)

    # 确认密钥输入提示标签
    confirm_key_label = tk.Label(key_frame,
                                 text="确认密码：",
                                 font=(None, 12),
                                 fg="#555555",
                                 bg="#d9d9d9")
    confirm_key_label.pack(side=tk.LEFT, padx=(10, 8))
    # 确认密钥输入框（显示星号）
    confirm_key_var = tk.StringVar()
    confirm_key_entry = tk.Entry(key_frame,
                                   textvariable=confirm_key_var,
                                   font=(None, 11),
                                   fg="#000000",
                                   bg="#ffffff",
                                   relief="groove",
                                   bd=2,
                                   show="*")
    confirm_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    # 绑定确认密码输入框内容改变事件
    def on_confirm_key_change(event=None):
        if not parent.notebook.setting_value:
            mark_tab_modified(parent, True)
    confirm_key_entry.bind("<KeyRelease>", on_confirm_key_change)

    class NoteBook:
        """将容器内所有组件和绑定的变量对象赋值给类属性，方便外部统一访问"""
        def __init__(self):
            # 文本编辑器
            self.text_editor = text_editor
            # 滚动条
            self.text_scroll = text_scroll
            # 密钥输入框
            self.key_entry = key_entry
            # 密钥变量
            self.key_var = key_var
            # 确认密钥输入框
            self.confirm_key_entry = confirm_key_entry
            # 确认密钥变量
            self.confirm_key_var = confirm_key_var
            # 关闭按钮
            self.close_btn = close_btn
            # 编辑器区域框架
            self.editor_frame = editor_frame
            # 密钥区域框架
            self.key_frame = key_frame
            # 密钥提示标签
            self.key_label = key_label
            # 确认密钥提示标签
            self.confirm_key_label = confirm_key_label
            # 类型
            self.type = FrameType.TEXT
            # 标志位：控制是否应该触发修改标记
            self.setting_value = False
        
        def set_values_safely(self, text_content=None, key=None, confirm_key=None):
            """安全地设置值，不会触发修改标记"""
            self.setting_value = True
            try:
                if text_content is not None:
                    # 先重置 modified 标志，防止 delete/insert 触发事件
                    self.text_editor.edit_modified(False)
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert("1.0", text_content)
                    # 再次重置 modified 标志
                    self.text_editor.edit_modified(False)
                if key is not None:
                    self.key_var.set(key)
                if confirm_key is not None:
                    self.confirm_key_var.set(confirm_key)
            finally:
                self.setting_value = False
    
    parent.notebook = NoteBook()
