import codecs
from configparser import ConfigParser
import os
from pathlib import Path
import shlex
import sys
from tkinter import messagebox
from AppKit import NSScreen
import subprocess
from utils.area import Area
from utils.dependencies import DEPENDENCIES


def find_mode(id, modes):
    for mode in modes:
        if id == mode.id:
            return "{}x{}".format(mode.width, mode.height)

def monitor_areas():  # all that matters from this is list(mapObj[monitor index][1])[k]; this is the list of monitor dimensions
    areas: list[Area] = []
    for monitor in NSScreen.screens():
        areas.append(
            Area(
                0,
                0,
                monitor.frame().size.width,
                monitor.frame().size.height,
            )
        )

    return areas


def hide_file(path: Path):
    hidden_path = path.parent / f".{path.name}"
    if path.exists():
        path.rename(hidden_path)


def expose_file(path: Path):
    hidden_path = path.parent / f".{path.name}"
    if hidden_path.exists():
        hidden_path.rename(path)


def check_dependencies() -> tuple[list[DEPENDENCIES], str]:
    missing_dependencies: list[DEPENDENCIES] = []
    messages: list[str] = []
    try:
        subprocess.check_output(["which", "ffmpeg"])
    except Exception as e:
        missing_dependencies.append(DEPENDENCIES.FFMPEG)
        messages.append("Couldn't find dependency FFMPEG.")

    try:
        import sounddevice
    except Exception as e:
        if len(e.args) == 1 and e.args[0] == "PortAudio library not found":
            missing_dependencies.append(DEPENDENCIES.PORT_AUDIO)
            messages.append(
                f"{e.args[0]}(Search for: 'libportaudio2' or 'libportaudio-dev')"
            )

    message = ""
    if messages:
        message = "\n".join((f"- {msg}" for msg in messages))
        messagebox.showerror("Missing dependencies", message)

    return missing_dependencies, message


first_run = True


def set_wallpaper(wallpaper_path: Path):
    global first_run
    if isinstance(wallpaper_path, Path):
        wallpaper_path = str(wallpaper_path.absolute())

    # Modified source from (Martin Hansen): https://stackoverflow.com/a/21213504
    # Note: There are two common Linux desktop environments where
    # I have not been able to set the desktop background from
    # command line: KDE, Enlightenment
    try:
        
        SCRIPT = """/usr/bin/osascript<<END
tell application "Finder"
set desktop picture to POSIX file "%s"
end tell
END"""

        subprocess.Popen(SCRIPT%wallpaper_path, shell=True)

        if first_run:
            first_run = False
        return True
    except:
        sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
        return False


# Source(geekpradd): PyWallpapyer https://github.com/geekpradd/PyWallpaper/blob/cc69a2784109d27100c3ecabb336e5bba8a1d923/PyWallpaper.py#L17
def get_output(command):
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    out, _ = p.communicate()
    return out


# Source(Martin Hansen, Serge Stroobandt): https://stackoverflow.com/a/21213358
def _get_desktop_environment():
    return "mac"

def does_desktop_shortcut_exists(name: str):
    file = Path(name)
    return Path(
        os.path.expanduser("~/Desktop") / file.with_name(f"{file.name}.desktop")
    ).exists()


def make_shortcut(
    path: Path,
    icon: str,
    script_or_command: str,
    title: str,
) -> bool:
    if title is None:
        if isinstance(script_or_command, str):
            title = script_or_command
        elif isinstance(icon, str):
            title = icon
        else:
            title = icon.name.replace("_icon", "")

    if isinstance(icon, str):
        icon = path / "default_assets" / f"{icon}_icon.ico"

    file_name = title.lower()

    if isinstance(script_or_command, str):
        script_path = str((path / f"{script_or_command}").absolute())
        script_or_command = [sys.executable, script_path]

    shortcut_content = f"""[Desktop Entry]
    Version=1.0
    Name={title}
    Exec={shlex.join(script_or_command)}
    Icon={str(icon.absolute())}
    Terminal=false
    Type=Application
    Categories=Application;
    """

    file_name = f"{file_name}.desktop"
    desktop_file = Path(os.path.expanduser("~/Desktop")) / file_name
    try:
        desktop_file.write_text(shortcut_content)
        if _get_desktop_environment() == "gnome":
            subprocess.run(
                [
                    "gio",
                    "set",
                    str(desktop_file.absolute()),
                    "metadata::trusted",
                    "true",
                ]
            )
    except:
        return False
    return True


# FIXME: Shouldn't be started with profile as it is not made to launch GUI application.
# Another problem is that VSCODE run .profile, and so run edgeware on start. Tempfix
def toggle_run_at_startup(path: Path, state: bool):
    command = f"{sys.executable} {str((path / 'start.pyw').absolute())}&"

    edgeware_content = f"""############## EDGEWARE ##############
if [[ ! "${{GIO_LAUNCHED_DESKTOP_FILE}}" == "/usr/share/applications/code.desktop" ]] && [[ ! "${{TERM_PROGRAM}}" == "vscode" ]]; then
    {command}
fi
############## EDGEWARE ##############
"""

    edgeware_profile = Path(os.path.expanduser("~/.profile"))

    profile = edgeware_profile.read_text()
    edgeware_profile.with_name(".profile_ew_backup").write_text(profile)

    if state:
        profile += edgeware_content
    else:
        profile = profile.replace(edgeware_content, "")
    edgeware_profile.write_text(profile)
