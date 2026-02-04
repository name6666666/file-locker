from tkinter import ttk
from ui.notebook import remove_tab
from muitimedia.picture import Image
from ui.frames.frame_type import FrameType



def picture_frame(parent: ttk.Frame, image_bytes: bytes):
    parent.configure(style="1.TFrame")
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    close_btn.config(command=lambda: remove_tab(parent))
    
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, pady=(34, 0))
    
    image_viewer = Image(main_frame, image_bytes=image_bytes)
    image_viewer.pack(fill="both", expand=True)
    
    def on_resize(event):
        if event.widget == main_frame:
            width = event.width
            height = event.height
            if width > 1 and height > 1:
                image_viewer.update_image(image_bytes, width=width, height=height)
    
    main_frame.bind("<Configure>", on_resize)
    
    class NoteBook:
        def __init__(self):
            self.close_btn = close_btn
            self.image_viewer = image_viewer
            self.type = FrameType.PICTURE
    
    parent.notebook = NoteBook()
    
    return parent
