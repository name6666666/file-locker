from tkinter import messagebox, filedialog, BooleanVar
from pathlib import Path
from multithread import threadfunc
from encrip import decrip
from ui.ask import ask_password
from ui.waiting import WaitWindow
from ui.notebook import add_tab, switch_to_tab, mark_tab_modified
from ui.frames.text_frame import build_text_frame
from ui.frames.audio_frame import audio_frame
from ui.frames.video_frame import video_frame
from ui.frames.picture_frame import picture_frame
from muitimedia.video import is_vlc_available


AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".aiff", ".au"
}
VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"
}
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".svg", ".webp", ".ico"
}


ENCRYPTED_AUDIO_EXTENSIONS = {".enc" + ext[1:] for ext in AUDIO_EXTENSIONS}
ENCRYPTED_VIDEO_EXTENSIONS = {".enc" + ext[1:] for ext in VIDEO_EXTENSIONS}
ENCRYPTED_IMAGE_EXTENSIONS = {".enc" + ext[1:] for ext in IMAGE_EXTENSIONS}


def text_frame(name, path=None):
    frame = add_tab(name)
    build_text_frame(frame)
    switch_to_tab(frame)
    frame.notebook.path = path
    return frame


@threadfunc(daemon=True)
def open_file():
    file_path = filedialog.askopenfilename(
        title="选择要打开的加密文件",
        filetypes=[("加密文件", "*.enc*")]
    )
    if file_path:
        ext = Path(file_path).suffix.lower()
        if not ext.startswith(".enc"):
            messagebox.showerror("错误", "文件扩展名无法识别")
            return
        if ext == ".enctxt":
            key = ask_password()
            if not key: return
            retain = BooleanVar(value=True)
            ww = WaitWindow("解密中", f'正在解密"{file_path}"', 1)
            def on_close():
                if messagebox.askyesno("停止解密", "确定停止解密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            try:
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                decription = decrip(encrypted_data, key)
                for _ in range(7):
                    ww.config(current_count=ww.current_count+1/7)
                    if not retain.get(): ww.destroy();return
                    next(decription)
                content = next(decription)[0].decode("utf-8")
            except Exception as e:
                messagebox.showerror("错误", "密码错误或文件已损坏")
                print(e)
                ww.destroy()
                return
            ww.destroy()
            tab = text_frame(Path(file_path).name, file_path)
            tab.notebook.set_values_safely(text_content=content, key=key, confirm_key=key)
            mark_tab_modified(tab, False)

            
        elif ext in ENCRYPTED_AUDIO_EXTENSIONS:
            key = ask_password()
            if not key: return
            retain = BooleanVar(value=True)
            ww = WaitWindow("解密中", f'正在解密音频文件"{file_path}"', 1)
            def on_close():
                if messagebox.askyesno("停止解密", "确定停止解密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            try:
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                decription = decrip(encrypted_data, key)
                for _ in range(7):
                    ww.config(current_count=ww.current_count+1/7)
                    if not retain.get(): ww.destroy();return
                    next(decription)
                audio_data = next(decription)[0]
            except Exception as e:
                messagebox.showerror("错误", "密码错误或文件已损坏")
                print(e)
                ww.destroy()
                return
            ww.destroy()
            tab = add_tab(Path(file_path).name)
            audio_frame(tab, audio_data, filename=Path(file_path).name)
            switch_to_tab(tab)
        elif ext in ENCRYPTED_VIDEO_EXTENSIONS:
            if not is_vlc_available():
                messagebox.showerror(
                    "视频播放功能不可用",
                    "未安装 VLC Media Player\n\n"
                    "请下载并安装 VLC Media Player 以启用视频播放功能\n"
                    "安装后请重启程序"
                )
                return
            key = ask_password()
            if not key: return
            retain = BooleanVar(value=True)
            ww = WaitWindow("解密中", f'正在解密视频文件"{file_path}"', 1)
            def on_close():
                if messagebox.askyesno("停止解密", "确定停止解密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            try:
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                decription = decrip(encrypted_data, key)
                for _ in range(7):
                    ww.config(current_count=ww.current_count+1/7)
                    if not retain.get(): ww.destroy();return
                    next(decription)
                video_data = next(decription)[0]
            except Exception as e:
                messagebox.showerror("错误", "密码错误或文件已损坏")
                print(e)
                ww.destroy()
                return
            ww.destroy()
            original_ext = ext.replace(".enc", "")
            tab = add_tab(Path(file_path).name)
            video_frame(tab, video_data, extension=original_ext)
            switch_to_tab(tab)
        elif ext in ENCRYPTED_IMAGE_EXTENSIONS:
            key = ask_password()
            if not key: return
            retain = BooleanVar(value=True)
            ww = WaitWindow("解密中", f'正在解密图片文件"{file_path}"', 1)
            def on_close():
                if messagebox.askyesno("停止解密", "确定停止解密吗？"):
                    retain.set(False)
            ww.set_on_close(on_close)
            try:
                with open(file_path, "rb") as f:
                    encrypted_data = f.read()
                decription = decrip(encrypted_data, key)
                for _ in range(7):
                    ww.config(current_count=ww.current_count+1/7)
                    if not retain.get(): ww.destroy();return
                    next(decription)
                image_data = next(decription)[0]
            except Exception as e:
                messagebox.showerror("错误", "密码错误或文件已损坏")
                print(e)
                ww.destroy()
                return
            ww.destroy()
            tab = add_tab(Path(file_path).name)
            picture_frame(tab, image_data)
            switch_to_tab(tab)
        else:
            messagebox.showerror("错误", "不支持的文件类型")
