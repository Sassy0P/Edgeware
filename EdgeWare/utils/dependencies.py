from enum import Enum


class DEPENDENCIES(str, Enum):
    FFMPEG = "FFMPEG"
    PORT_AUDIO = "PortAudio"
    XLIB = "Xlib"
    PYAUDIO = "PyAudio"
    TKINTER = "tkinter"
    WHEEL = 'wheel'
