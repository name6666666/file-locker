from tkinter import ttk
from ui.notebook import remove_tab
from muitimedia.video import BytecodeVideoPlayer
from ui.frames.frame_type import FrameType



def video_frame(parent: ttk.Frame, video_bytes: bytes, extension: str = ".mp4"):
    parent.configure(style="1.TFrame")
    
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, pady=(34, 0))
    
    video_player = BytecodeVideoPlayer(main_frame, bytecode=video_bytes, extension=extension)
    video_player.pack(fill="both", expand=True)
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    close_btn.config(command=lambda: (video_player.release(), remove_tab(parent)))
    
    class NoteBook:
        def __init__(self):
            self.close_btn = close_btn
            self.video_player = video_player
            self.type = FrameType.VIDEO
    
    parent.notebook = NoteBook()
    
    return parent
