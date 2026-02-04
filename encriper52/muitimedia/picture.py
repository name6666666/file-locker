from tkinter import ttk, Canvas
from io import BytesIO
from PIL import Image as PILImage, ImageTk


class Image(ttk.Frame):
    """
    从字节码加载图片并创建内嵌 tkinter 的图片组件
    """

    def __init__(self, master=None, image_bytes: bytes = None, *, width: int = None, height: int = None, **kwargs):
        """
        构造参数
        :param master: 父容器
        :param image_bytes: 图片字节码
        :param width: 指定宽度，若仅指定其一则高度按比例自适应
        :param height: 指定高度，若仅指定其一则宽度按比例自适应
        :param kwargs: 其他 ttk.Frame 支持的参数
        """
        super().__init__(master, **kwargs)
        self._image_bytes = image_bytes
        self._width = width
        self._height = height
        self._photo_image = None
        self._canvas = None
        self._load_image()
        self._create_widget()

    def _load_image(self):
        """从字节码加载图片并转换为 tkinter 可用的 PhotoImage，支持按比例缩放"""
        if not self._image_bytes:
            self._photo_image = None
            return
        try:
            image_stream = BytesIO(self._image_bytes)
            pil_image = PILImage.open(image_stream)
            # 若指定了宽或高，则按比例缩放
            if self._width is not None or self._height is not None:
                orig_w, orig_h = pil_image.size
                if self._width is not None and self._height is None:
                    # 仅指定宽度，按比例计算高度
                    ratio = self._width / orig_w
                    new_h = int(orig_h * ratio)
                    pil_image = pil_image.resize((self._width, new_h), PILImage.Resampling.LANCZOS)
                elif self._height is not None and self._width is None:
                    # 仅指定高度，按比例计算宽度
                    ratio = self._height / orig_h
                    new_w = int(orig_w * ratio)
                    pil_image = pil_image.resize((new_w, self._height), PILImage.Resampling.LANCZOS)
                else:
                    # 两者均指定，按比例缩放并保持宽高比
                    scale_w = self._width / orig_w
                    scale_h = self._height / orig_h
                    scale = min(scale_w, scale_h)
                    new_w = int(orig_w * scale)
                    new_h = int(orig_h * scale)
                    pil_image = pil_image.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
            self._photo_image = ImageTk.PhotoImage(pil_image)
        except Exception as e:
            self._photo_image = None
            print(f"图片加载失败: {e}")

    def _create_widget(self):
        """创建内嵌 Canvas 用于显示图片"""
        self._canvas = Canvas(self, bg="white", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        if self._photo_image:
            # 计算居中位置
            canvas_width = self._canvas.winfo_width()
            canvas_height = self._canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                # 获取图片尺寸
                img_width = self._photo_image.width()
                img_height = self._photo_image.height()
                # 计算居中偏移
                x_offset = (canvas_width - img_width) // 2
                y_offset = (canvas_height - img_height) // 2
                self._canvas.create_image(x_offset, y_offset, anchor="nw", image=self._photo_image)
            else:
                self._canvas.create_image(0, 0, anchor="nw", image=self._photo_image)
        
        def on_canvas_resize(event):
            if event.widget == self._canvas and self._photo_image:
                self._canvas.delete("all")
                canvas_width = event.width
                canvas_height = event.height
                img_width = self._photo_image.width()
                img_height = self._photo_image.height()
                x_offset = (canvas_width - img_width) // 2
                y_offset = (canvas_height - img_height) // 2
                self._canvas.create_image(x_offset, y_offset, anchor="nw", image=self._photo_image)
        
        self._canvas.bind("<Configure>", on_canvas_resize)

    def update_image(self, new_image_bytes: bytes, width: int = None, height: int = None):
        """
        更新图片
        :param new_image_bytes: 新的图片字节码
        :param width: 新宽度，可省略以使用原宽度设置
        :param height: 新高度，可省略以使用原高度设置
        """
        self._image_bytes = new_image_bytes
        # 若调用时重新指定了宽或高，则更新
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height
        self._load_image()
        if self._photo_image:
            # 清除画布并重新绘制
            self._canvas.delete("all")
            canvas_width = self._canvas.winfo_width()
            canvas_height = self._canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                img_width = self._photo_image.width()
                img_height = self._photo_image.height()
                x_offset = (canvas_width - img_width) // 2
                y_offset = (canvas_height - img_height) // 2
                self._canvas.create_image(x_offset, y_offset, anchor="nw", image=self._photo_image)
            else:
                self._canvas.create_image(0, 0, anchor="nw", image=self._photo_image)


