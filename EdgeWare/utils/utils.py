import os
import sys
from enum import Enum
import subprocess
import playsound
from typing import Union

import EdgeWare
import EdgeWare.popup
from EdgeWare.utils.dependencies import DEPENDENCIES


def is_windows() -> bool:
    return "win32" in sys.platform


def is_linux() -> bool:
    return "linux" in sys.platform


if is_linux():
    from EdgeWare.utils.linux import *
elif is_windows():
    from EdgeWare.utils.windows import *
else:
    raise RuntimeError("Unsupported operating system: {}".format(sys.platform))


class SCRIPTS(str, Enum):
    DISCORD_HANDLER = "disc_handler.py"
    POPUP = "popup.py"
    PANIC = "panic.py"


def run_script(*args: Union[str, SCRIPTS]):
    popen_args = [sys.executable, *args]
    test = os.environ
    test.update({"PYTHONPATH": ":".join(sys.path)})
    subprocess.Popen(popen_args, env=test)


def run_discord_handler_script(*args: str):
    run_script(SCRIPTS.DISCORD_HANDLER.value, *args)


def run_popup_script(*args: str):
    run_script(SCRIPTS.POPUP.value, *args)


def run_panic_script(*args: str):
    run_script(SCRIPTS.PANIC.value, *args)


def play_soundfile(filepath: str, block=False):
    playsound.playsound(filepath, block)
