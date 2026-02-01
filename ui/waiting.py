import tkinter as tk
from tkinter import ttk
from threading import Event
from queue import Queue
from typing import Optional, List, Dict, Any



class WaitWindow:
    """
    等待窗口类，用于在后台操作时显示进度和处理用户交互
    
    该类提供了一个美观的等待窗口，可以显示进度条、错误信息和选项对话框
    所有 GUI 操作都在主线程中执行，确保线程安全
    """
    
    def __init__(self, title: str, description: str, total_count: int, current_count: float=0):
        """
        初始化等待窗口
        
        Args:
            title: 窗口标题
            description: 窗口描述信息
            total_count: 总计数
            current_count: 当前计数
        """
        self.title: str = title
        self.description: str = description
        self.total_count: int = total_count
        self.current_count: float = current_count
        self.window: Optional[tk.Toplevel] = None
        self.progress_var: Optional[tk.DoubleVar] = None
        self._event: Event = Event()
        self._queue: Queue = Queue()
        self._result: Optional[str] = None
        self._message_frame: Optional[ttk.Frame] = None
        self._separator: Optional[ttk.Separator] = None
        self._on_close_callback: Optional[callable] = None
        
        # 配置样式
        self._configure_styles()
        
        # 使用主线程的事件循环来创建窗口
        self._create_window_in_main_thread()

    def _configure_styles(self) -> None:
        """
        配置 ttk 样式
        """
        # 配置 ttk 样式
        style = ttk.Style()
        
        # 主窗口样式
        style.configure("WaitWindow.TFrame", padding=20)
        
        # 描述标签样式
        style.configure("Description.TLabel", wraplength=380, padding=5)
        
        # 计数标签样式
        style.configure("Count.TLabel", padding=5)
        
        # 进度条样式
        style.configure("WaitProgress.Horizontal.TProgressbar")
        
        # 消息区域样式
        style.configure("Message.TFrame", padding=15)
        
        # 按钮样式
        style.configure("Action.TButton", padding=10, foreground="#000000")
        style.configure("Choice.TButton", padding=10, foreground="#000000")

    def _create_window_in_main_thread(self) -> None:
        """
        在主线程中创建窗口
        """
        # 确保在主线程中创建窗口
        def create() -> None:
            self._create_window()
        
        if tk._default_root:
            tk._default_root.after(0, create)
        else:
            # 如果没有默认根窗口，直接创建
            self._create_window()

    def _create_window(self) -> None:
        """
        创建窗口
        """
        self.window = tk.Toplevel()
        self.window.title(self.title)
        self.window.geometry("450x200")  # 更小的初始窗口尺寸
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # 设置窗口背景色
        self.window.configure(bg="#f8f8f8")

        main_frame = ttk.Frame(self.window, style="WaitWindow.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 描述区域
        self.description_label = ttk.Label(main_frame, text=self.description, style="Description.TLabel")
        self.description_label.pack(pady=(0, 15))

        # 分割线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))

        # 进度条区域
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_var = tk.DoubleVar(value=self.current_count / self.total_count * 100)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, style="WaitProgress.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X)

        self.count_label = ttk.Label(main_frame, text=f"{self.current_count:.2f}/{self.total_count}", style="Count.TLabel")
        self.count_label.pack(pady=(0, 10))

        # 开始处理队列
        self._process_queue()

    def _on_close(self) -> None:
        """
        窗口关闭事件处理
        """
        if self._on_close_callback:
            self._on_close_callback()


    def _process_queue(self) -> None:
        """
        处理队列中的消息
        """
        try:
            while True:
                item = self._queue.get_nowait()
                if item[0] == "error":
                    _, title, description = item
                    self._show_error_in_window(title, description)
                elif item[0] == "choice":
                    _, title, description, choices = item
                    self._show_choice_in_window(title, description, choices)
                elif item[0] == "config":
                    _, kwargs = item
                    self._update_config(kwargs)
                elif item[0] == "destroy":
                    self._destroy_window()
        except:
            pass
        if self.window:
            self.window.after(100, self._process_queue)

    def _clear_message_frame(self) -> None:
        """
        清空消息区域
        """
        # 清空消息区域
        if self._message_frame:
            for widget in self._message_frame.winfo_children():
                widget.destroy()
            self._message_frame.pack_forget()
            self._message_frame = None
        
        # 移除分割线
        if self._separator:
            self._separator.pack_forget()
            self._separator = None
        
        # 恢复窗口到初始大小
        self.window.geometry("450x200")
        self.window.update()

    def _show_error_in_window(self, title: str, description: str) -> None:
        """
        在窗口中显示错误信息
        
        Args:
            title: 错误标题
            description: 错误描述
        """
        # 清空消息区域
        self._clear_message_frame()
        
        # 添加分割线
        main_frame = self.window.winfo_children()[0]
        self._separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        self._separator.pack(fill=tk.X, pady=(15, 0))
        
        # 创建消息区域
        self._message_frame = ttk.Frame(main_frame, style="Message.TFrame")
        self._message_frame.pack(fill=tk.BOTH, expand=True)
        
        # 调整窗口大小以容纳错误信息
        self.window.geometry("450x350")
        self.window.update()
        
        # 分割线
        ttk.Separator(self._message_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))
        
        # 显示错误标题
        ttk.Label(self._message_frame, text=title, font=(None, 11, 'bold')).pack(pady=(0, 10))
        
        # 显示错误描述
        ttk.Label(self._message_frame, text=description, wraplength=380).pack(pady=(0, 20))
        
        # 显示确认按钮
        def on_error_ok() -> None:
            self._clear_message_frame()
            self._result = None
            self._event.set()
        
        button_frame = ttk.Frame(self._message_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(button_frame, text="确定", command=on_error_ok).pack(pady=10)

    def _show_choice_in_window(self, title: str, description: str, choices: List[str]) -> None:
        """
        在窗口中显示选择
        
        Args:
            title: 选择标题
            description: 选择描述
            choices: 选项列表
        """
        # 清空消息区域
        self._clear_message_frame()
        
        # 添加分割线
        main_frame = self.window.winfo_children()[0]
        self._separator = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        self._separator.pack(fill=tk.X, pady=(15, 0))
        
        # 创建消息区域
        self._message_frame = ttk.Frame(main_frame, style="Message.TFrame")
        self._message_frame.pack(fill=tk.BOTH, expand=True)
        
        # 根据按钮数量动态调整窗口大小
        window_height = 320 + (len(choices) - 1) * 40
        self.window.geometry(f"450x{window_height}")
        self.window.update()
        
        # 分割线
        ttk.Separator(self._message_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 15))
        
        # 显示选择标题
        ttk.Label(self._message_frame, text=title, font=(None, 11, 'bold')).pack(pady=(0, 10))
        
        # 显示选择描述
        ttk.Label(self._message_frame, text=description, wraplength=380).pack(pady=(0, 20))
        
        # 显示选择按钮
        button_frame = ttk.Frame(self._message_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        def on_choice_selected(choice: str) -> None:
            self._clear_message_frame()
            self._result = choice
            self._event.set()
        
        for i, choice in enumerate(choices):
            btn = ttk.Button(button_frame, text=choice, command=lambda c=choice: on_choice_selected(c))
            btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

    def _update_config(self, kwargs: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            kwargs: 配置参数
        """
        if "current_count" in kwargs:
            self.current_count = kwargs["current_count"]
            if self.window and self.progress_var:
                self.progress_var.set(self.current_count / self.total_count * 100)
                if hasattr(self, 'count_label'):
                    self.count_label.config(text=f"{self.current_count:.2f}/{self.total_count}")
        
        if "description" in kwargs:
            self.description = kwargs["description"]
            if self.window and hasattr(self, 'description_label'):
                self.description_label.config(text=self.description)

    def _destroy_window(self) -> None:
        """
        销毁窗口
        """
        if self.window:
            self.window.destroy()
            self.window = None

    def set_on_close(self, callback: Optional[callable]) -> None:
        """
        设置窗口关闭按钮（点叉）触发的回调函数
        
        Args:
            callback: 关闭时调用的函数，传入 None 则清除回调
        """
        self._on_close_callback = callback

    def close_current_display(self) -> None:
        """
        关闭当前展示的错误或选择对话框，恢复到初始状态
        """
        if not self.window:
            return
        
        def close_in_main_thread() -> None:
            self._clear_message_frame()
            self._result = None
            self._event.set()
        
        if tk._default_root:
            tk._default_root.after(0, close_in_main_thread)
        else:
            close_in_main_thread()

    def showerror(self, title: str, description: str, close_var: Optional[tk.BooleanVar] = None) -> Optional[None]:
        """
        显示错误信息
        
        Args:
            title: 错误标题
            description: 错误描述
            close_var: 可选的 BoolVar 对象，当值变为 False 时自动关闭
            
        Returns:
            None
        """
        if not self.window:
            return None
        
        self._event.clear()
        self._queue.put(("error", title, description))
        
        # 监听 close_var 的变化
        def check_close_var():
            if close_var and not close_var.get():
                self.close_current_display()
                return
            if not self._event.is_set():
                if tk._default_root:
                    tk._default_root.after(100, check_close_var)
        
        if close_var:
            check_close_var()
        
        self._event.wait()
        return self._result

    def showchoice(self, title: str, description: str, choices: List[str], close_var: Optional[tk.BooleanVar] = None) -> Optional[str]:
        """
        显示选择
        
        Args:
            title: 选择标题
            description: 选择描述
            choices: 选项列表
            close_var: 可选的 BoolVar 对象，当值变为 False 时自动关闭
            
        Returns:
            用户选择的选项
        """
        if not self.window:
            return None
        
        self._event.clear()
        self._queue.put(("choice", title, description, choices))
        
        # 监听 close_var 的变化
        def check_close_var():
            if close_var and not close_var.get():
                self.close_current_display()
                return
            if not self._event.is_set():
                if tk._default_root:
                    tk._default_root.after(100, check_close_var)
        
        if close_var:
            check_close_var()
        
        self._event.wait()
        return self._result

    def config(self, **kwargs: Any) -> None:
        """
        配置窗口
        
        Args:
            **kwargs: 配置参数
        """
        if not self.window:
            return
        self._queue.put(("config", kwargs))

    def destroy(self) -> None:
        """
        销毁窗口
        """
        self._queue.put(("destroy",))
