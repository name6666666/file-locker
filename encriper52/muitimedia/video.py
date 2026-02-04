import threading
import tempfile
import os
import atexit
import signal
import weakref
from tkinter import ttk, Label, Button
import sys

_vlc_available = False
_vlc_import_error = None

try:
    import vlc
    _vlc_available = True
except ImportError as e:
    _vlc_import_error = str(e)
except Exception as e:
    _vlc_import_error = f"VLC 加载失败: {str(e)}"

_temp_files_registry = set()
_cleanup_registered = False


def is_vlc_available():
    """检查 VLC 是否可用"""
    return _vlc_available


def get_vlc_error():
    """获取 VLC 错误信息"""
    return _vlc_import_error


def _cleanup_all_temp_files():
    """清理所有注册的临时文件"""
    global _temp_files_registry
    for temp_path in list(_temp_files_registry):
        try:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
    _temp_files_registry.clear()


def _register_cleanup_handlers():
    """注册程序退出时的清理处理器"""
    global _cleanup_registered
    if _cleanup_registered:
        return
    _cleanup_registered = True
    
    atexit.register(_cleanup_all_temp_files)
    
    import sys
    if sys.platform != 'win32':
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, lambda s, f: (_cleanup_all_temp_files(), signal.default_int_handler(s, f)))
            except Exception:
                pass
    else:
        try:
            import win32api
            def console_handler(ctrl_type):
                if ctrl_type in (win32api.CTRL_C_EVENT, win32api.CTRL_CLOSE_EVENT, 
                                win32api.CTRL_LOGOFF_EVENT, win32api.CTRL_SHUTDOWN_EVENT):
                    _cleanup_all_temp_files()
                    return False
                return True
            win32api.SetConsoleCtrlHandler(console_handler, True)
        except ImportError:
            pass
        except Exception:
            pass


_register_cleanup_handlers()




class _VLCBytecodeVideoPlayer(ttk.Frame):
    """
    基于 VLC 的视频播放器类
    支持从字节码加载视频，使用临时文件
    """

    def __init__(self, master=None, bytecode: bytes = None, extension: str = ".mp4", **kwargs):
        """
        构造方法
        :param master: 父容器
        :param bytecode: 视频字节码
        :param extension: 视频文件扩展名，用于 VLC 识别格式
        :param kwargs: 其他 ttk.Frame 支持的参数
        """
        super().__init__(master, **kwargs)
        self._bytecode = bytecode
        self._extension = extension
        self._vlc_instance = None
        self._media_player = None
        self._media = None
        self._is_playing = False
        self._is_paused = False
        self._total_duration = 0
        self._current_time = 0
        self._lock = threading.Lock()
        self._temp_file = None
        self._temp_file_path = None
        self._finalizer = None
        self._setup_vlc()
        self._create_widget()
        self._load_video()
        self._register_finalizer()

    def _register_finalizer(self):
        """注册弱引用终结器，确保对象被垃圾回收时清理资源"""
        def cleanup_callback(temp_path):
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    _temp_files_registry.discard(temp_path)
            except Exception:
                pass
        
        if self._temp_file_path:
            self._finalizer = weakref.finalize(self, cleanup_callback, self._temp_file_path)

    def _setup_vlc(self):
        """初始化 VLC 实例"""
        try:
            self._vlc_instance = vlc.Instance()
            self._media_player = self._vlc_instance.media_player_new()
        except Exception as e:
            print(f"VLC 初始化失败: {e}")
            raise

    def _create_widget(self):
        """创建视频播放窗口"""
        try:
            self._media_player.set_hwnd(self.winfo_id())
        except Exception as e:
            print(f"设置播放窗口失败: {e}")

    def _load_video(self):
        """从字节码加载视频"""
        if not self._bytecode:
            return
        
        try:
            self._cleanup_temp_file()
            suffix = self._extension if self._extension.startswith('.') else f'.{self._extension}'
            self._temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=suffix)
            self._temp_file.write(self._bytecode)
            self._temp_file.close()
            self._temp_file_path = self._temp_file.name
            
            _temp_files_registry.add(self._temp_file_path)
            
            self._media = self._vlc_instance.media_new(self._temp_file_path)
            self._media_player.set_media(self._media)
            self._media.parse()
            self._total_duration = self._media.get_duration() / 1000.0
            
            self._register_finalizer()
        except Exception as e:
            print(f"视频加载失败: {e}")
            self._cleanup_temp_file()

    def _cleanup_temp_file(self):
        """清理临时文件"""
        if self._temp_file_path:
            if self._temp_file_path in _temp_files_registry:
                _temp_files_registry.discard(self._temp_file_path)
            try:
                if os.path.exists(self._temp_file_path):
                    os.unlink(self._temp_file_path)
            except Exception as e:
                print(f"清理临时文件失败: {e}")
            finally:
                self._temp_file_path = None
        self._temp_file = None
        if self._finalizer:
            try:
                self._finalizer.detach()
            except Exception:
                pass
            self._finalizer = None

    def play(self):
        """播放视频"""
        with self._lock:
            if self._media_player:
                if self._is_paused:
                    self._media_player.pause()
                    self._is_paused = False
                else:
                    self._media_player.play()
                self._is_playing = True

    def pause(self):
        """暂停播放"""
        with self._lock:
            if self._media_player and self._is_playing:
                self._media_player.pause()
                self._is_paused = True

    def stop(self):
        """停止播放"""
        with self._lock:
            if self._media_player:
                self._media_player.stop()
                self._is_playing = False
                self._is_paused = False
                self._current_time = 0

    def seek_forward(self, seconds: float = 5.0):
        """快进指定秒数"""
        with self._lock:
            if self._media_player:
                current_time = self._media_player.get_time() / 1000.0
                new_time = min(current_time + seconds, self._total_duration)
                self._media_player.set_time(int(new_time * 1000))

    def seek_backward(self, seconds: float = 5.0):
        """回退指定秒数"""
        with self._lock:
            if self._media_player:
                current_time = self._media_player.get_time() / 1000.0
                new_time = max(current_time - seconds, 0)
                self._media_player.set_time(int(new_time * 1000))

    def jump_to(self, seconds: float):
        """跳转到指定秒数"""
        with self._lock:
            if self._media_player:
                new_time = max(0, min(seconds, self._total_duration))
                self._media_player.set_time(int(new_time * 1000))

    def get_current_position(self) -> float:
        """获取当前播放位置（秒）"""
        if self._media_player:
            return self._media_player.get_time() / 1000.0
        return 0.0

    def get_total_duration(self) -> float:
        """获取视频总时长（秒）"""
        return self._total_duration

    def set_volume(self, volume: float):
        """设置音量"""
        volume = max(0, min(100, volume * 100))
        if self._media_player:
            self._media_player.audio_set_volume(int(volume))

    def get_volume(self) -> float:
        """获取当前音量"""
        if self._media_player:
            return self._media_player.audio_get_volume() / 100.0
        return 1.0

    def set_fullscreen(self, fullscreen: bool):
        """设置全屏"""
        if self._media_player:
            self._media_player.set_fullscreen(fullscreen)

    def toggle_fullscreen(self):
        """切换全屏"""
        if self._media_player:
            self._media_player.toggle_fullscreen()

    def get_state(self):
        """获取播放状态"""
        if self._media_player:
            return self._media_player.get_state()
        return None

    def is_playing(self) -> bool:
        """是否正在播放"""
        return self._is_playing and not self._is_paused

    def is_paused(self) -> bool:
        """是否暂停"""
        return self._is_paused

    def update_video(self, new_bytecode: bytes, extension: str = None):
        """更新视频"""
        with self._lock:
            was_playing = self._is_playing and not self._is_paused
            self.stop()
            self._bytecode = new_bytecode
            if extension is not None:
                self._extension = extension
            self._load_video()
            if was_playing:
                self.play()

    def release(self):
        """释放资源"""
        with self._lock:
            self._is_playing = False
            self._is_paused = False
            if self._media_player:
                self._media_player.stop()
                self._media_player.release()
                self._media_player = None
            if self._media:
                self._media.release()
                self._media = None
            if self._vlc_instance:
                self._vlc_instance.release()
                self._vlc_instance = None
            self._cleanup_temp_file()

    def __del__(self):
        """析构函数，确保资源被释放"""
        try:
            self.release()
        except:
            pass


BytecodeVideoPlayer = _VLCBytecodeVideoPlayer
