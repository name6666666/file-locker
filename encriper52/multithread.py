from threading import Thread, current_thread
from typing import Callable




def threadfunc(group: None = None,
               name: str | None = None,
               *,
               daemon: bool | None = None) -> Callable:
    def decorator(func):
        def wrapper(*args, **kwargs):
            th = Thread(group=group, target=func, name=name, args=args, kwargs=kwargs, daemon=daemon)
            th.start()
            return th
        return wrapper
    return decorator
