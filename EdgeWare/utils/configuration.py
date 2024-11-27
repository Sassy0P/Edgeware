from dataclasses import dataclass
import dataclasses
import json
import logging
from pathlib import Path
from re import I
import sys
from typing import Any, ClassVar, Dict, List, Literal, Optional, Type, Union
from annotated_types import T
import pydantic

from EdgeWare.ui import configuration

CONFIG_PATH = Path(__file__, "..", "..", "config.json").resolve()
DEFAULT_AVOID_LIST = ["EdgeWare", "AppData"]
DEFAULT_WALLPAPERDAT = {"default": "wallpaper.png"}

__DEV__ = True
__VERSION__ = "2.4.2"

if __DEV__:
    __VERSION__ += "_DEV"


# TODO: Version migration system
# TODO: Check against last version
@pydantic.dataclasses.dataclass(
    validate_on_init=True,
    config=pydantic.ConfigDict(extra="forbid", validate_assignment=True),
)
class Configuration:
    version: str = __VERSION__
    delay: int = 1000
    fill: bool = False
    replace: bool = False
    webMod: int = pydantic.Field(ge=0, le=100, default=20)
    popupMod: int = pydantic.Field(ge=0, le=100, default=20)
    audioMod: int = pydantic.Field(ge=0, le=100, default=20)
    promptMod: int = pydantic.Field(ge=0, le=100, default=20)
    vidMod: int = pydantic.Field(ge=0, le=100, default=20)
    replaceThresh: int = 500
    slowMode: int = 0
    pip_installed: int = 0
    is_configured: bool = False
    fill_delay: int = 0
    start_on_logon: bool = False
    hibernateMode: bool = False
    hibernateMin: int = 240
    hibernateMax: int = 300
    wakeupActivity: int = 20
    pypres_installed: int = 0
    showDiscord: bool = False
    pil_installed: int = 0
    showLoadingFlair: bool = True
    showCaptions: bool = False
    maxFillThreads: int = 8
    panicButton: str = "e"
    panicDisabled: bool = False
    promptMistakes: int = 3
    squareLim: int = 800
    mitosisMode: bool = False
    onlyVid: bool = False
    webPopup: bool = False
    rotateWallpaper: bool = False
    wallpaperTimer: int = 30
    wallpaperVariance: int = 0
    timeoutPopups: bool = False
    popupTimeout: int = 0
    mitosisStrength: int = 2
    avoidList: List[str] = pydantic.Field(default=DEFAULT_AVOID_LIST)
    booruName: str = ""
    booruMinScore: int = -5
    tagList: List[str] = pydantic.Field(default=["all"])
    downloadEnabled: bool = False
    downloadMode: str = "All"
    useWebResource: bool = False
    runOnSaveQuit: bool = False
    timerMode: bool = False
    timerSetupTime: int = 0
    safeword: str = "password"
    lkCorner: int = 0
    lkScaling: int = 100
    lkToggle: bool = False
    videoVolume: int = 25
    denialMode: bool = False
    denialChance: int = 0
    popupSubliminals: int = 0
    drivePath: str = "C:/Users/"
    wallpaperDat: Dict[str, str] = pydantic.Field(default=DEFAULT_WALLPAPERDAT)

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            raise e

    def as_dict(self) -> "dict[str, Any]":
        return dataclasses.asdict(self)

    def update(self, **kwargs):
        # TODO: Would be nice to only validate after all assignements.
        for name, value in kwargs.items():
            setattr(self, name, value)

    @classmethod
    def load(
        cls: Type[T], load_path: Optional[str] = None, panic_on_error: bool = False
    ) -> Optional[T]:
        configuration_path = Path(load_path or CONFIG_PATH)
        log_cmd = logging.error if panic_on_error else logging.info
        try:
            return cls(**json.loads(configuration_path.read_text()))
        except pydantic.ValidationError as e:
            log_cmd(
                f"Could'nt load configuration from '{configuration_path}' for the following reason(s):"
            )

            for error in e.errors():
                log_cmd(f" - {error['loc'][0]}: {error['msg']}")
                log_cmd(
                    f" \t- Awaited type: '{error['type']}' got '{type(error['input'])}' => '{error['input']}'"
                )
            log_cmd(
                f"If you didn't edit the configs files/scripts please report it has bugs with your logs. Thank you."
            )
            if panic_on_error:
                raise e
        except FileNotFoundError as e:
            log_cmd(f"Couldn't find the configuration file at '{configuration_path}'")
            if panic_on_error:
                raise e

    @classmethod
    def load_or_default(
        cls, load_path: Optional[str] = None, enable_log: bool = False
    ) -> "Configuration":
        configuration = cls.load(load_path)
        if not configuration:
            logging.info("No config.json found. Using default configuration")
        return configuration or cls()

    @classmethod
    def from_dat(cls: Type[T], dat_data: str) -> T:
        fields, values = [line.split(",") for line in dat_data.splitlines()]
        data: Dict[str, Any] = dict(zip(fields, values))

        data["avoidList"] = data["avoidList"].split(">")
        if data["wallpaperDat"] == "WPAPER_DEF":
            data["wallpaperDat"] = DEFAULT_WALLPAPERDAT

        return cls(**data)

    def save(self, path: Optional[str] = None):
        Path(path or CONFIG_PATH).write_text(json.dumps(self.as_dict(), indent=4))

    def __getitem__(self, key: Any, default: Any = None) -> Any:
        return getattr(self, key, default)  # type: ignore

    def __setitem__(self, key: Any, value: Any):
        setattr(self, key, value)

    def get(self, key: Any, default=None):
        return self.__getitem__(key, default)


DEFAULT_CONFIGURATION = Configuration()


def __GENERATE_ENUM():
    enum_template = """
from enum import Enum

class ConfigurationFields(Enum):
"""
    # TEMP: Pascal case to Snake_Case
    # https://stackoverflow.com/a/1176023
    import re

    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    convert = lambda s: pattern.sub("_", s).upper()

    for field in DEFAULT_CONFIGURATION.as_dict().keys():
        enum_template += f'\t{convert(field)} = "{field}"\n'

    enum_file = Path(__file__).parent / "configuration_enum.py"
    enum_file.write_text(enum_template)


if __name__ == "__main__":
    __GENERATE_ENUM()
