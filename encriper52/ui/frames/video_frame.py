from tkinter import ttk
import tkinter as tk
from ui.notebook import remove_tab
from muitimedia.video import BytecodeVideoPlayer, is_vlc_available
from ui.frames.frame_type import FrameType



def video_frame(parent: ttk.Frame, video_bytes: bytes, extension: str = ".mp4", filename: str = ""):
    parent.configure(style="1.TFrame")
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    
    top_distance = 34
    
    main_frame = tk.Frame(parent, bg="black")
    main_frame.pack(fill="both", expand=True, pady=(top_distance, 0))
    
    video_player = BytecodeVideoPlayer(main_frame, bytecode=video_bytes, extension=extension)
    video_player.pack(fill="both", expand=True)
    
    control_frame = None
    progress_scale = None
    time_label = None
    play_pause_btn = None
    stop_btn = None
    backward_btn = None
    forward_btn = None
    volume_scale = None
    volume_label = None
    
    if is_vlc_available():
        control_frame = tk.Frame(main_frame, bg="#2c2c2c", height=60)
        control_frame.pack(fill="x", side="bottom")
        
        progress_frame = tk.Frame(control_frame, bg="#2c2c2c")
        progress_frame.pack(fill="x", padx=10, pady=(5, 0))
        
        progress_scale = ttk.Scale(progress_frame, orient="horizontal", from_=0, to=100)
        progress_scale.pack(fill="x")
        
        time_label = tk.Label(progress_frame, text="0:00 / 0:00", font=(None, 8), bg="#2c2c2c", fg="#cccccc")
        time_label.pack(pady=(2, 0))
        
        buttons_frame = tk.Frame(control_frame, bg="#2c2c2c")
        buttons_frame.pack(pady=(5, 10))
        
        backward_btn = ttk.Button(buttons_frame, text="◀ 5s", width=6)
        backward_btn.pack(side="left", padx=3)
        
        play_pause_btn = ttk.Button(buttons_frame, text="▶", width=5)
        play_pause_btn.pack(side="left", padx=3)
        
        stop_btn = ttk.Button(buttons_frame, text="■", width=5)
        stop_btn.pack(side="left", padx=3)
        
        forward_btn = ttk.Button(buttons_frame, text="5s ▶", width=6)
        forward_btn.pack(side="left", padx=3)
        
        volume_scale = ttk.Scale(buttons_frame, orient="horizontal", from_=0, to=100, length=80)
        volume_scale.set(100)
        volume_scale.pack(side="left", padx=(20, 5))
        
        volume_label = tk.Label(buttons_frame, text="100%", font=(None, 8), bg="#2c2c2c", fg="#cccccc")
        volume_label.pack(side="left")
    
    if is_vlc_available():
        def format_time(seconds):
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}:{secs:02d}"
        
        def update_time_label():
            current_seconds = video_player.get_current_position()
            total_seconds = video_player.get_total_duration()
            time_label.config(text=f"{format_time(current_seconds)} / {format_time(total_seconds)}")
        
        def update_progress():
            total_duration = video_player.get_total_duration()
            if total_duration > 0:
                current_position = video_player.get_current_position()
                progress_value = (current_position / total_duration) * 100
                progress_scale.set(progress_value)
        
        def on_play_pause():
            if video_player.is_playing():
                video_player.pause()
                play_pause_btn.config(text="▶")
            else:
                video_player.play()
                play_pause_btn.config(text="⏸")
        
        def on_stop():
            video_player.stop()
            play_pause_btn.config(text="▶")
            progress_scale.set(0)
            update_time_label()
        
        def on_backward():
            video_player.seek_backward(5.0)
            update_progress()
            update_time_label()
        
        def on_forward():
            video_player.seek_forward(5.0)
            update_progress()
            update_time_label()
        
        def on_volume_change(value):
            volume_percent = float(value)
            volume_percent = max(0, min(100, volume_percent))
            volume_value = volume_percent / 100.0
            video_player.set_volume(volume_value)
            volume_label.config(text=f"{int(volume_percent)}%")
        
        def on_seek(value):
            total_duration = video_player.get_total_duration()
            if total_duration > 0:
                target_seconds = float(value) * total_duration / 100
                video_player.jump_to(target_seconds)
                update_time_label()
        
        def on_scale_press(event):
            nonlocal is_dragging
            is_dragging = True
        
        def on_scale_drag(event):
            if is_dragging:
                scale_width = progress_scale.winfo_width()
                x = event.x
                value = (x / scale_width) * 100
                value = max(0, min(100, value))
                progress_scale.set(value)
                total_duration = video_player.get_total_duration()
                if total_duration > 0:
                    target_seconds = (value / 100) * total_duration
                    time_label.config(text=f"{format_time(target_seconds)} / {format_time(total_duration)}")
        
        def on_scale_release(event):
            nonlocal is_dragging
            if is_dragging:
                is_dragging = False
                value = progress_scale.get()
                total_duration = video_player.get_total_duration()
                if total_duration > 0:
                    target_seconds = (value / 100) * total_duration
                    video_player.jump_to(target_seconds)
                update_time_label()
        
        is_active = True
        is_dragging = False
        
        def update_progress_loop():
            if is_active and not is_dragging:
                update_progress()
                update_time_label()
                current_position = video_player.get_current_position()
                total_duration = video_player.get_total_duration()
                if total_duration > 0 and current_position >= total_duration and not video_player.is_paused():
                    video_player.stop()
                    play_pause_btn.config(text="▶")
                    progress_scale.set(0)
                    update_time_label()
            control_frame.after(5, update_progress_loop)
        
        play_pause_btn.config(command=on_play_pause)
        stop_btn.config(command=on_stop)
        backward_btn.config(command=on_backward)
        forward_btn.config(command=on_forward)
        
        volume_scale.config(command=on_volume_change)
        
        progress_scale.bind("<ButtonPress-1>", on_scale_press)
        progress_scale.bind("<B1-Motion>", on_scale_drag)
        progress_scale.bind("<ButtonRelease-1>", on_scale_release)
        
        update_time_label()
        update_progress_loop()
    
    def on_close():
        video_player.release()
        remove_tab(parent)
    
    close_btn.config(command=on_close)
    
    class NoteBook:
        def __init__(self):
            self.video_player = video_player
            self.close_btn = close_btn
            self.play_pause_btn = play_pause_btn
            self.stop_btn = stop_btn
            self.backward_btn = backward_btn
            self.forward_btn = forward_btn
            self.progress_scale = progress_scale
            self.time_label = time_label
            self.volume_scale = volume_scale
            self.volume_label = volume_label
            self.type = FrameType.VIDEO
    
    parent.notebook = NoteBook()
    
    return parent
