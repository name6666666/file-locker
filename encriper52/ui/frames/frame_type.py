from enum import Enum

class FrameType(Enum):
    TEXT = 0
    ENC_ANY = 1
    AUDIO = 2
    PICTURE = 3
    VIDEO = 4
    WELCOME = 5
    SPACE = 6