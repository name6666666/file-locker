import io
import pyaudio
import threading
import soundfile as sf
import numpy as np



class AudioPlayer:
    """
    音频播放器类
    支持从字节码加载音频，并提供播放、暂停、快进、回退、跳转、关闭等功能
    """

    def __init__(self, audio_bytes: bytes):
        """
        构造方法，接收字节码音频数据
        :param audio_bytes: 音频字节码
        """
        self.audio_bytes = audio_bytes
        self.audio_data = None
        self.sample_rate = None
        self.channels = None
        self.pyaudio_instance = None
        self.stream = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.total_samples = 0
        self.play_lock = threading.Lock()
        self.position_lock = threading.Lock()
        self.play_thread = None
        self.chunk_size = 65536
        self._load_audio()

    def _load_audio(self):
        """从字节码加载音频数据"""
        try:
            audio_stream = io.BytesIO(self.audio_bytes)
            self.audio_data, self.sample_rate = sf.read(audio_stream, always_2d=True)
            if len(self.audio_data.shape) == 1:
                self.audio_data = self.audio_data.reshape(-1, 1)
            self.channels = self.audio_data.shape[1]
            self.audio_data = (self.audio_data * 32767).astype(np.int16)
            self.total_samples = self.audio_data.shape[0]
        except Exception as e:
            print(f"音频加载失败: {e}")
            raise

    def _check_audio_device(self):
        """检查是否有可用的音频输出设备"""
        try:
            if self.pyaudio_instance is None:
                self.pyaudio_instance = pyaudio.PyAudio()
            device_count = self.pyaudio_instance.get_device_count()
            if device_count == 0:
                raise OSError("没有可用的音频设备")
            
            for i in range(device_count):
                try:
                    device_info = self.pyaudio_instance.get_device_info_by_index(i)
                    if device_info['maxOutputChannels'] > 0:
                        return True
                except:
                    continue
            raise OSError("没有可用的音频输出设备")
        except Exception as e:
            print(f"音频设备检查失败: {e}")
            raise

    def _play_worker(self):
        """
        播放线程工作函数
        """
        try:
            self._check_audio_device()
            
            with self.play_lock:
                if self.stream is not None:
                    self.stream.stop_stream()
                    self.stream.close()
                self.stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True,
                    frames_per_buffer=self.chunk_size
                )
                self.is_playing = True
                self.is_paused = False

            while True:
                with self.play_lock:
                    if not self.is_playing or self.is_paused:
                        break
                
                with self.position_lock:
                    if self.position >= self.total_samples:
                        break
                    current_pos = self.position
                    chunk = self.audio_data[current_pos:current_pos + self.chunk_size]
                    chunk_len = chunk.shape[0]
                    self.position = current_pos + chunk_len
                
                if chunk_len == 0:
                    break
                
                self.stream.write(chunk.tobytes())

            with self.play_lock:
                self.is_playing = False
                if self.stream is not None:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
        except Exception as e:
            print(f"播放失败: {e}")
            with self.play_lock:
                self.is_playing = False
                self.is_paused = False
                if self.stream is not None:
                    try:
                        self.stream.stop_stream()
                        self.stream.close()
                    except:
                        pass
                    self.stream = None

    def play(self):
        """
        播放音频
        """
        try:
            with self.play_lock:
                if self.is_playing and not self.is_paused:
                    return
                if self.is_paused:
                    self.is_paused = False
                    self.is_playing = True
                    self.play_lock.release()
                    self.play_thread = threading.Thread(target=self._play_worker, daemon=True)
                    self.play_thread.start()
                    self.play_lock.acquire()
                    return
            self.play_thread = threading.Thread(target=self._play_worker, daemon=True)
            self.play_thread.start()
        except Exception as e:
            print(f"播放启动失败: {e}")

    def pause(self):
        """
        暂停播放
        """
        with self.play_lock:
            if self.is_playing and not self.is_paused:
                self.is_paused = True

    def resume(self):
        """
        恢复播放
        """
        with self.play_lock:
            if self.is_playing and self.is_paused:
                self.is_paused = False
                self.is_playing = True
                self.play_lock.release()
                self.play_thread = threading.Thread(target=self._play_worker, daemon=True)
                self.play_thread.start()
                self.play_lock.acquire()

    def stop(self):
        """
        停止播放，但不释放资源
        """
        with self.play_lock:
            self.is_playing = False
            self.is_paused = False
            with self.position_lock:
                self.position = 0
            if self.stream is not None:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                self.stream = None
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)

    def seek_forward(self, seconds: float = 5.0):
        """
        快进指定秒数
        :param seconds: 快进的秒数，默认5秒
        """
        with self.play_lock:
            if self.audio_data is None:
                return
            samples = int(seconds * self.sample_rate)
            with self.position_lock:
                new_pos = min(self.position + samples, self.total_samples)
                self.position = new_pos
            was_playing = self.is_playing and not self.is_paused
            self.is_playing = False
            self.is_paused = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
        if was_playing:
            self.play()

    def seek_backward(self, seconds: float = 5.0):
        """
        回退指定秒数
        :param seconds: 回退的秒数，默认5秒
        """
        with self.play_lock:
            if self.audio_data is None:
                return
            samples = int(seconds * self.sample_rate)
            with self.position_lock:
                new_pos = max(self.position - samples, 0)
                self.position = new_pos
            was_playing = self.is_playing and not self.is_paused
            self.is_playing = False
            self.is_paused = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
        if was_playing:
            self.play()

    def jump_to(self, seconds: float):
        """
        跳转到指定秒数
        :param seconds: 目标秒数
        """
        with self.play_lock:
            if self.audio_data is None:
                return
            new_pos = int(seconds * self.sample_rate)
            new_pos = max(0, min(new_pos, self.total_samples))
            with self.position_lock:
                self.position = new_pos
            was_playing = self.is_playing and not self.is_paused
            self.is_playing = False
            self.is_paused = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
        if was_playing:
            self.play()

    def get_current_position(self):
        """
        获取当前播放位置（秒）
        :return: 当前播放位置（秒）
        """
        if self.sample_rate and self.sample_rate > 0:
            return self.position / self.sample_rate
        return 0.0

    def get_total_duration(self):
        """
        获取音频总时长（秒）
        :return: 音频总时长（秒）
        """
        if self.sample_rate and self.sample_rate > 0:
            return self.total_samples / self.sample_rate
        return 0.0

    def close(self):
        """
        关闭播放器，释放资源
        """
        with self.play_lock:
            self.is_playing = False
            self.is_paused = False
            if self.stream is not None:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                self.stream = None
            if self.play_thread and self.play_thread.is_alive():
                self.play_lock.release()
                self.play_thread.join(timeout=1.0)
                self.play_lock.acquire()
            if self.pyaudio_instance:
                try:
                    self.pyaudio_instance.terminate()
                except:
                    pass
                self.pyaudio_instance = None
            self.audio_data = None

    def __del__(self):
        """
        析构函数，确保资源被释放
        """
        try:
            self.close()
        except:
            pass
