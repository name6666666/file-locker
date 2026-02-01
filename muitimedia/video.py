import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk
import threading
import time
import io
import imageio
from typing import Optional, Any


class BytecodeVideoPlayer(tk.Frame):
    """
    从字节码加载视频，并在 tkinter 界面中播放。
    提供播放/暂停、进度条、音量、全屏等完整操作功能。
    """

    def __init__(self, parent: tk.Widget, bytecode: Optional[bytes] = None, extension: str = ".mp4", **kwargs: Any) -> None:
        super().__init__(parent, **kwargs)
        self.parent: tk.Widget = parent
        self.bytecode: Optional[bytes] = bytecode
        self.extension: str = extension
        self.video_reader = None
        self.frames = []
        self.current_frame_idx = 0
        self.running: bool = False
        self.paused: bool = False
        self.frame_delay: int = 0
        self.total_frames: int = 0
        self.fps: float = 0
        self.temp_file_path: Optional[str] = None

        self.canvas: Optional[tk.Canvas] = None
        self.control_frame: Optional[ttk.Frame] = None
        self.play_btn: Optional[ttk.Button] = None
        self.progress: Optional[ttk.Scale] = None
        self.volume_scale: Optional[ttk.Scale] = None
        self.fullscreen_btn: Optional[ttk.Button] = None
        self.status_lbl: Optional[ttk.Label] = None

        self._build_ui()
        if self.bytecode:
            self.load_bytecode(self.bytecode)

    # -------------------- 字节码加载 --------------------
    def load_bytecode(self, bytecode, extension: str = None):
        """从字节码加载视频"""
        self.bytecode = bytecode
        if extension:
            self.extension = extension
        self._load_video_from_memory()

    def _load_video_from_memory(self):
        """从内存加载视频"""
        try:
            import tempfile
            import os
            
            video_stream = io.BytesIO(self.bytecode)
            
            suffix = self.extension if self.extension and self.extension.startswith('.') else f'.{self.extension}' if self.extension else '.mp4'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(self.bytecode)
                self.temp_file_path = temp_file.name
            
            self.video_reader = imageio.get_reader(self.temp_file_path)
            self.total_frames = len(self.video_reader)
            self.fps = self.video_reader.get_meta_data().get('fps', 30)
            self.frame_delay = int(1000 / self.fps)
            self._set_status("视频加载成功")
            self._update_progress_max()
            self._play_loop()
        except Exception as e:
            self._set_status(f"加载失败: {e}")
            print(f"视频加载失败: {e}")

    # -------------------- UI 构建 --------------------
    def _build_ui(self):
        """构建主界面"""
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(fill="x", padx=5, pady=5)

        # 播放/暂停
        self.play_btn = ttk.Button(self.control_frame, text="播放", command=self.toggle_play_pause)
        self.play_btn.pack(side="left", padx=5)

        # 进度条
        self.progress = ttk.Scale(self.control_frame, orient="horizontal", command=self._on_seek)
        self.progress.pack(fill="x", side="left", expand=True, padx=5)

        # 音量
        ttk.Label(self.control_frame, text="音量:").pack(side="left", padx=(10, 0))
        self.volume_scale = ttk.Scale(self.control_frame, orient="horizontal", from_=0, to=100, value=50, command=self._on_volume_change)
        self.volume_scale.pack(side="left", padx=5)

        # 全屏
        self.fullscreen_btn = ttk.Button(self.control_frame, text="全屏", command=self.toggle_fullscreen)
        self.fullscreen_btn.pack(side="left", padx=5)

        # 状态标签
        self.status_lbl = ttk.Label(self.control_frame, text="就绪")
        self.status_lbl.pack(side="right", padx=5)

        # 绑定键盘
        self.parent.bind("<space>", lambda e: self.toggle_play_pause())
        self.parent.bind("<Escape>", lambda e: self.exit_fullscreen())

    # -------------------- 播放控制 --------------------
    def toggle_play_pause(self):
        """切换播放/暂停"""
        if not self.video_reader:
            return
        self.paused = not self.paused
        self.play_btn.config(text="播放" if self.paused else "暂停")

    def _on_seek(self, value):
        """拖动进度条跳转"""
        if not self.video_reader:
            return
        self.current_frame_idx = int(float(value) * self.total_frames / 100)

    def _on_volume_change(self, value):
        """音量调节（占位，实际音频需额外库）"""
        # 这里仅做 UI 展示，实际音量控制需结合音频库
        pass

    def toggle_fullscreen(self):
        """进入全屏"""
        self.winfo_toplevel().attributes("-fullscreen", True)

    def exit_fullscreen(self):
        """退出全屏"""
        self.winfo_toplevel().attributes("-fullscreen", False)

    # -------------------- 播放循环 --------------------
    def _play_loop(self):
        """后台线程播放视频帧"""
        def run():
            self.running = True
            while self.running:
                if self.video_reader and not self.paused:
                    if self.current_frame_idx < self.total_frames:
                        try:
                            frame = self.video_reader.get_data(self.current_frame_idx)
                        except Exception as e:
                            print(f"读取帧失败: {e}")
                            self.paused = True
                            self.play_btn.config(text="播放")
                            break
                        
                        # 获取画布大小
                        canvas_width = self.canvas.winfo_width()
                        canvas_height = self.canvas.winfo_height()
                        if canvas_width > 1 and canvas_height > 1:
                            # 获取原始帧尺寸
                            frame_h, frame_w = frame.shape[:2]
                            # 计算缩放比例，保持宽高比
                            scale_w = canvas_width / frame_w
                            scale_h = canvas_height / frame_h
                            scale = min(scale_w, scale_h)
                            # 计算缩放后的尺寸
                            new_w = int(frame_w * scale)
                            new_h = int(frame_h * scale)
                            # 缩放帧
                            frame = cv2.resize(frame, (new_w, new_h))
                            # 计算居中位置
                            x_offset = (canvas_width - new_w) // 2
                            y_offset = (canvas_height - new_h) // 2
                            # imageio 返回的帧已经是 RGB 格式，直接使用
                            image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                            # 清除画布并绘制居中的图像
                            self.canvas.delete("all")
                            self.canvas.create_image(x_offset, y_offset, anchor="nw", image=image)
                            self.canvas.image = image  # 防止被回收
                        # 更新进度条
                        progress_value = (self.current_frame_idx / self.total_frames) * 100
                        self.progress.set(progress_value)
                        self.current_frame_idx += 1
                    else:
                        # 播放结束
                        self.paused = True
                        self.play_btn.config(text="播放")
                        self.current_frame_idx = 0
                time.sleep(self.frame_delay / 1000)
        threading.Thread(target=run, daemon=True).start()

    # -------------------- 辅助 --------------------
    def _update_progress_max(self):
        """设置进度条范围"""
        self.progress.config(from_=0, to=100)

    def _set_status(self, text):
        """更新状态栏文字"""
        self.status_lbl.config(text=text)

    def release(self):
        """释放资源"""
        self.running = False
        if self.video_reader:
            try:
                self.video_reader.close()
            except Exception:
                pass
            self.video_reader = None
        if self.temp_file_path:
            try:
                import os
                os.unlink(self.temp_file_path)
            except Exception:
                pass
            self.temp_file_path = None
