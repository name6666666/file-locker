from muitimedia.audio import AudioPlayer
from tkinter import ttk
import tkinter as tk
from ui.notebook import remove_tab
from ui.frames.frame_type import FrameType



def audio_frame(parent: tk.Frame | ttk.Frame, audio: bytes):
    parent.configure(style="1.TFrame")
    
    player = AudioPlayer(audio)
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, pady=(34, 0))
    
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill="x", padx=10, pady=10)
    
    play_pause_btn = ttk.Button(control_frame, text="播放", width=8)
    play_pause_btn.pack(side="left", padx=5)
    
    stop_btn = ttk.Button(control_frame, text="停止", width=8)
    stop_btn.pack(side="left", padx=5)
    
    ttk.Separator(control_frame, orient="vertical").pack(side="left", fill="y", padx=10)
    
    backward_btn = ttk.Button(control_frame, text="<< 5s", width=8)
    backward_btn.pack(side="left", padx=5)
    
    forward_btn = ttk.Button(control_frame, text="5s >>", width=8)
    forward_btn.pack(side="left", padx=5)
    
    progress_frame = ttk.Frame(main_frame)
    progress_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    progress_scale = ttk.Scale(progress_frame, orient="horizontal", from_=0, to=100)
    progress_scale.pack(fill="x", side="left", expand=True)
    
    time_label = ttk.Label(progress_frame, text="0:00 / 0:00")
    time_label.pack(side="left", padx=(10, 0))
    
    status_label = ttk.Label(main_frame, text="就绪")
    status_label.pack(side="bottom", anchor="w", padx=10, pady=(0, 5))
    
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    def update_time_label():
        current_seconds = player.get_current_position()
        total_seconds = player.get_total_duration()
        time_label.config(text=f"{format_time(current_seconds)} / {format_time(total_seconds)}")
    
    def update_progress():
        total_duration = player.get_total_duration()
        if total_duration > 0:
            current_position = player.get_current_position()
            progress_value = (current_position / total_duration) * 100
            progress_scale.set(progress_value)
    
    def on_play_pause():
        if player.is_playing and not player.is_paused:
            player.pause()
            play_pause_btn.config(text="播放")
            status_label.config(text="已暂停")
        else:
            player.play()
            play_pause_btn.config(text="暂停")
            status_label.config(text="播放中")
    
    def on_stop():
        player.stop()
        play_pause_btn.config(text="播放")
        status_label.config(text="已停止")
        progress_scale.set(0)
        update_time_label()
    
    def on_backward():
        player.seek_backward(5.0)
        update_progress()
        update_time_label()
    
    def on_forward():
        player.seek_forward(5.0)
        update_progress()
        update_time_label()
    
    def on_seek(value):
        total_duration = player.get_total_duration()
        if total_duration > 0:
            target_seconds = float(value) * total_duration / 100
            player.jump_to(target_seconds)
            update_time_label()
    
    is_active = True
    
    def update_progress_loop():
        if is_active:
            update_progress()
            update_time_label()
            main_frame.after(100, update_progress_loop)
    
    def on_close():
        nonlocal is_active
        is_active = False
        player.close()
        remove_tab(parent)
    
    close_btn.config(command=on_close)
    
    play_pause_btn.config(command=on_play_pause)
    stop_btn.config(command=on_stop)
    backward_btn.config(command=on_backward)
    forward_btn.config(command=on_forward)
    progress_scale.config(command=on_seek)
    
    update_time_label()
    update_progress_loop()
    
    class NoteBook:
        def __init__(self):
            self.player = player
            self.close_btn = close_btn
            self.play_pause_btn = play_pause_btn
            self.stop_btn = stop_btn
            self.backward_btn = backward_btn
            self.forward_btn = forward_btn
            self.progress_scale = progress_scale
            self.time_label = time_label
            self.status_label = status_label
            self.type = FrameType.AUDIO
    
    parent.notebook = NoteBook()
    
    return parent
