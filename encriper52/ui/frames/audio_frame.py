from muitimedia.audio import AudioPlayer
from tkinter import ttk
import tkinter as tk
from ui.notebook import remove_tab
from ui.frames.frame_type import FrameType



def audio_frame(parent: tk.Frame | ttk.Frame, audio: bytes, filename: str = ""):
    parent.configure(style="1.TFrame")
    
    player = AudioPlayer(audio)
    
    close_btn = ttk.Button(parent, text="X")
    close_btn.place(x=5, y=5, width=24, height=24)
    
    top_distance = 34
    
    main_frame = tk.Frame(parent, bg="white")
    main_frame.pack(fill="both", expand=True, pady=(top_distance, 0))
    
    center_frame = tk.Frame(main_frame, bg="white")
    center_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    icon_canvas = tk.Canvas(center_frame, width=120, height=120, highlightthickness=0, bg="white")
    icon_canvas.pack(pady=(0, 20))
    
    icon_canvas.create_oval(20, 20, 100, 100, fill="#4a90d9", outline="#2c5aa0", width=2)
    icon_canvas.create_text(60, 60, text="♪", font=(None, 48), fill="white")
    
    filename_label = tk.Label(center_frame, text=filename, font=(None, 10), bg="white", fg="#555555")
    filename_label.pack(pady=(0, 20))
    
    progress_frame = tk.Frame(center_frame, bg="white")
    progress_frame.pack(fill="x", pady=(0, 15))
    
    progress_scale = ttk.Scale(progress_frame, orient="horizontal", from_=0, to=100, length=300)
    progress_scale.pack(side="left", expand=True)
    
    time_label = tk.Label(progress_frame, text="0:00 / 0:00", font=(None, 9), bg="white")
    time_label.pack(side="left", padx=(10, 0))
    
    control_frame = tk.Frame(center_frame, bg="white")
    control_frame.pack(pady=(0, 10))
    
    backward_btn = ttk.Button(control_frame, text="◀ 5s", width=8)
    backward_btn.pack(side="left", padx=5)
    
    play_pause_btn = ttk.Button(control_frame, text="▶ 播放", width=10)
    play_pause_btn.pack(side="left", padx=5)
    
    stop_btn = ttk.Button(control_frame, text="■ 停止", width=8)
    stop_btn.pack(side="left", padx=5)
    
    forward_btn = ttk.Button(control_frame, text="5s ▶", width=8)
    forward_btn.pack(side="left", padx=5)
    
    volume_frame = tk.Frame(center_frame, bg="white")
    volume_frame.pack(pady=(0, 10))
    
    volume_icon_canvas = tk.Canvas(volume_frame, width=24, height=24, highlightthickness=0, bg="white")
    volume_icon_canvas.pack(side="left", padx=(0, 10))
    volume_icon_canvas.create_polygon(4, 8, 4, 16, 12, 12, fill="#555555")
    volume_icon_canvas.create_line(14, 8, 14, 16, fill="#555555", width=1)
    volume_icon_canvas.create_line(17, 6, 17, 18, fill="#555555", width=1)
    volume_icon_canvas.create_line(20, 4, 20, 20, fill="#555555", width=1)
    
    volume_scale = ttk.Scale(volume_frame, orient="horizontal", from_=0, to=100, length=200)
    volume_scale.set(100)
    volume_scale.pack(side="left")
    
    volume_label = tk.Label(volume_frame, text="100%", font=(None, 9), bg="white", fg="#555555")
    volume_label.pack(side="left", padx=(10, 0))
    
    status_label = tk.Label(center_frame, text="就绪", font=(None, 9), bg="white")
    status_label.pack(pady=(15, 5))
    
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
            play_pause_btn.config(text="▶ 播放")
            status_label.config(text="已暂停")
        else:
            player.play()
            play_pause_btn.config(text="⏸ 暂停")
            status_label.config(text="播放中")
    
    def on_stop():
        player.stop()
        play_pause_btn.config(text="▶ 播放")
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
    
    def on_volume_change(value):
        volume_percent = float(value)
        volume_percent = max(0, min(100, volume_percent))
        volume_value = volume_percent / 100.0
        player.set_volume(volume_value)
        volume_label.config(text=f"{int(volume_percent)}%")
    
    def on_seek(value):
        total_duration = player.get_total_duration()
        if total_duration > 0:
            target_seconds = float(value) * total_duration / 100
            player.jump_to(target_seconds)
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
            total_duration = player.get_total_duration()
            if total_duration > 0:
                target_seconds = (value / 100) * total_duration
                time_label.config(text=f"{format_time(target_seconds)} / {format_time(total_duration)}")
    
    def on_scale_release(event):
        nonlocal is_dragging
        if is_dragging:
            is_dragging = False
            value = progress_scale.get()
            total_duration = player.get_total_duration()
            if total_duration > 0:
                target_seconds = (value / 100) * total_duration
                player.jump_to(target_seconds)
                update_time_label()
    
    is_active = True
    is_dragging = False
    
    def update_progress_loop():
        if is_active and not is_dragging:
            update_progress()
            update_time_label()
            current_position = player.get_current_position()
            total_duration = player.get_total_duration()
            if total_duration > 0 and current_position >= total_duration and not player.is_paused:
                player.stop()
                play_pause_btn.config(text="▶ 播放")
                status_label.config(text="已停止")
                progress_scale.set(0)
                update_time_label()
        center_frame.after(5, update_progress_loop)
    
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
    
    volume_scale.config(command=on_volume_change)
    
    progress_scale.bind("<ButtonPress-1>", on_scale_press)
    progress_scale.bind("<B1-Motion>", on_scale_drag)
    progress_scale.bind("<ButtonRelease-1>", on_scale_release)
    
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
            self.volume_scale = volume_scale
            self.volume_label = volume_label
            self.type = FrameType.AUDIO
    
    parent.notebook = NoteBook()
    
    return parent
