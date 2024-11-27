from dataclasses import dataclass
import getpass
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from typing import List, Optional, Union
import urllib.request
import webbrowser
import zipfile
from pathlib import Path
from tkinter import (
    DISABLED,
    GROOVE,
    RAISED,
    SINGLE,
    BooleanVar,
    Button,
    Checkbutton,
    Entry,
    Frame,
    IntVar,
    Label,
    Listbox,
    Misc,
    OptionMenu,
    Scale,
    StringVar,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
    simpledialog,
    ttk,
)

from pydantic import ValidationError

from EdgeWare.utils.configuration import DEFAULT_CONFIGURATION, Configuration
from EdgeWare.utils import utils
from EdgeWare.utils.configuration_enum import ConfigurationFields

PATH = Path(__file__).parent

# Starting logging
log_directory = PATH / "logs"
if not log_directory.exists():
    log_directory.mkdir(exist_ok=True, parents=True)


log_file = (
    log_directory / f"{time.asctime().replace(' ', '_').replace(':', '-')}-dbg.txt"
)
logging.basicConfig(
    filename=log_file,
    format="%(levelname)s:%(message)s",
    level=logging.DEBUG,
)
logging.info("Started start logging successfully.")


def pip_install(packageName: str):
    try:
        logging.info(f"attempting to install {packageName}")
        subprocess.run([sys.executable, "python" "-m", "pip", "install", packageName])
    except:
        logging.warning(
            f"failed to install {packageName} using py -m pip, trying raw pip request"
        )
        subprocess.run(["pip", "install", packageName])
        logging.warning(
            f"{packageName} should be installed, fatal errors will occur if install failed."
        )


try:
    import requests
except:
    pip_install("requests")
    import requests

try:
    import PIL
    from PIL import Image, ImageTk
except:
    logging.warning("failed to import pillow module")
    pip_install("pillow")
    from PIL import Image, ImageTk


SYS_ARGS = sys.argv.copy()
SYS_ARGS.pop(0)
logging.info(f"args: {SYS_ARGS}")

# text for the about tab
ANNOYANCE_TEXT = 'The "Annoyance" section consists of the 5 main configurable configuration of Edgeware:\nDelay\nPopup Frequency\nWebsite Frequency\nAudio Frequency\nPromptFrequency\n\nEach is fairly self explanatory, but will still be expounded upon in this section. Delay is the forced time delay between each tick of the "clock" for Edgeware. The longer it is, the slower things will happen. Popup frequency is the percent chance that a randomly selected popup will appear on any given tick of the clock, and similarly for the rest, website being the probability of opening a website or video from /resource/vid/, audio for playing a file from /resource/aud/, and prompt for a typing prompt to pop up.\n\nThese values can be set by adjusting the bars, or by clicking the button beneath each respective slider, which will allow you to type in an explicit number instead of searching for it on the scrollbar.\n\nIn order to disable any feature, lower its probability to 0, to ensure that you\'ll be getting as much of any feature as possible, turn it up to 100.\nThe popup setting "Mitosis mode" changes how popups are displayed. Instead of popping up based on the timer, the program create a single popup when it starts. When the submit button on ANY popup is clicked to close it, a number of popups will open up in its place, as given by the "Mitosis Strength" setting.\n\nPopup timeout will result in popups timing out and closing after a certain number of seconds.'
DRIVE_TEXT = 'The "Drive" portion of Edgeware has three features: fill drive, replace images, and Booru downloader.\n\n"Fill Drive" does exactly what it says: it attempts to fill your hard drive with as much porn from /resource/img/ as possible. It does, however, have some restrictions. It will (should) not place ANY images into folders that start with a "." or have their names listed in the folder name blacklist.\nIt will also ONLY place images into the User folder and its subfolders.\nFill drive has one modifier, which is its own forced delay. Because it runs with between 1 and 8 threads at any given time, when unchecked it can fill your drive VERY quickly. To ensure that you get that nice slow fill, you can adjust the delay between each folder sweep it performs and the max number of threads.\n\n"Replace Images" is more complicated. Its searching is the exact same as fill drive, but instead of throwing images everywhere, it will seek out folders with large numbers of images (more than the threshold value) and when it finds one, it will replace ALL of the images with porn from /resource/img/. REMEMBER THAT IF YOU CARE ABOUT YOUR PHOTOS, AND THEY\'RE IN A FOLDER WITH MORE IMAGES THAN YOUR CHOSEN THRESHOLD VALUE, EITHER BACK THEM UP IN A ZIP OR SOMETHING OR DO. NOT. USE. THIS SETTING. I AM NOT RESPONSIBLE FOR YOUR OWN DECISION TO RUIN YOUR PHOTOS.\n\nBooru downloader allows you to download new items from a Booru of your choice. For the booru name, ONLY the literal name is used, like "censored" or "blacked" instead of the full url. This is not case sensitive. Use the "Validate" button to ensure that downloading will be successful before running. For tagging, if you want to have mutliple tags, they can be combined using "tag1+tag2+tag3" or if you want to add blacklist tags, type your tag and append a "+-blacklist_tag" after the desired tag.'
STARTUP_TEXT = 'Start on launch does exactly what it says it does and nothing more: it allows Edgeware to start itself whenever you start up and log into your PC.\n\nPlease note that the method used does NOT edit registry or schedule any tasks. The "lazy startup" method was used for both convenience of implementation and convenience of cleaning.\n\nIf you forget to turn off the "start on logon" setting before uninstalling, you will need to manually go to your Startup folder and remove "edgeware.bat".'
WALLPAPER_TEXT = "The Wallpaper section allows you to set up rotating wallpapers of your choice from any location, or auto import all images from the /resource/ folder (NOT /resource/img/ folder) to use as wallpapers.\n\nThe rotate timer is the amount of time the program will wait before rotating to another randomly selected wallpaper, and the rotate variation is the amount above or below that set value that can randomly be selected as the actual wait time."
HIBERNATE_TEXT = 'The Hibernate feature is an entirely different mode for Edgeware to operate in.\nInstead of constantly shoving popups, lewd websites, audio, and prompts in your face, hibernate starts quiet and waits for a random amount of time between its provided min and max before exploding with a rapid assortment of your chosen payloads. Once it finishes its barrage, it settles back down again for another random amount of time, ready to strike again when the time is right.\n\n\nThis feature is intend to be a much "calmer" way to use Edgeware; instead of explicitly using it to edge yourself or get off, it\'s supposed to lie in wait for you and perform bursts of self-sabotage to keep drawing you back to porn.'
ADVANCED_TEXT = "The Advanced section is also something previously only accessible by directly editing the config.cfg file. It offers full and complete customization of all setting values without any limitations outside of variable typing.\n\n\nPlease use this feature with discretion, as any erroneous values will result in a complete deletion and regeneration of the config file from the default, and certain value ranges are likely to result in crashes or unexpected glitches in the program."
THANK_AND_ABOUT_TEXT = "Thank you so much to all the fantastic artists who create and freely distribute the art that allows programs like this to exist, to all the people who helped me work through the various installation problems as we set the software up (especially early on), and honestly thank you to ALL of the people who are happily using Edgeware. \n\nIt truly makes me happy to know that my work is actually being put to good use by people who enjoy it. After all, at the end of the day that's really all I've ever really wanted, but figured was beyond reach of a stupid degreeless neet.\nI love you all <3\n\n\n\nIf you like my work, please feel free to help support my neet lifestyle by donating to $PetitTournesol on Cashapp; by no means are you obligated or expected to, but any and all donations are greatly appreciated!"


# COLOR SCHEMES
@dataclass
class ColorScheme:
    DEFAULT = "SystemButtonFace" if os.name == "nt" else "gray90"


# all booru consts
BOORU_FLAG = "<BOORU_INSERT>"  # flag to replace w/ booru name
BOORU_URL = (
    f"https://{BOORU_FLAG}.booru.org/index.php?page=post&s=list&tags="  # basic url
)
BOORU_VIEW = (
    f"https://{BOORU_FLAG}.booru.org/index.php?page=post&s=view&id="  # post view url
)
BOORU_PTAG = "&pid="  # page id tag

# url to check online version
UPDCHECK_URL = "http://raw.githubusercontent.com/PetitTournesol/Edgeware/main/EdgeWare/configDefault.dat"
# local_version = "0.0.0_NOCONNECT"

# local_version = DEFAULT_CONFIGURATION.version

# if not config_file.exists():
#     logging.warning(
#         f"No '{CONFIG_PATH.name}' file found, creating new '{CONFIG_PATH.name}'."
#     )
#     DEFAULT_CONFIGURATION.save()
#     logging.info("Created new configuration file.")

# logging.info("Loading configuration file")
# try:
#     configuration = Configuration.load()
# except Exception as e:
#     logging.fatal(f"Could not load the configuration file.\n\nReason: {e}")
#     exit(-1)

# FIXME: Recheck new version models
# inserts new configuration if versions are literally different
# or if the count of configuration between actual and default is different
# if configuration.version != defaultVars[0] or len(configuration) != len(defaultconfiguration):
#     logging.warning(
#         "version difference/settingJson len mismatch, regenerating new configuration with missing keys..."
#     )
#     tempSettingDict = {}
#     for name in varNames:
#         try:
#             tempSettingDict[name] = configuration[name]
#         except:

#             tempSettingDict[name] = defaultVars[varNames.index(name)]
#             logging.info(f"added missing key: {name}")
#     tempSettingDict["version"] = defaultVars[0]
#     configuration = tempSettingDict.copy()
#     # bugfix for the config crash issue
#     tempSettingDict["wallpaperDat"] = str(tempSettingDict["wallpaperDat"]).replace(
#         "'", "%^%"
#     )
#     tempconfigurationtring = str(tempSettingDict).replace("'", '"')
#     config_file.write_text(tempconfigurationtring.replace("%^%", "'"))
#    logging.info("wrote regenerated configuration.")


pass_ = ""


def open_configuration() -> Configuration:
    configuration = Configuration.load_or_default(enable_log=True)
    web_version = get_live_version()

    # window things
    root = Tk()
    root.title("Edgeware Config")
    root.geometry("740x675")
    try:
        img = Image.open(str((PATH / "default_assets" / "config_icon.ico").absolute()))
        icon = ImageTk.PhotoImage(img)
        root.iconbitmap(icon)
    except Exception as e:
        logging.warning("Failed to set iconbitmap.")

    variables = {}
    var = lambda x: variables[x.value]
    var_get = lambda x: var(x).get()

    def update_var(name, _, __):
        configuration[name] = variables[name].get()

    for name, value in configuration.as_dict().items():
        if isinstance(value, int):
            var_type = IntVar  # variables[name] = IntVar(root, value)
        elif isinstance(value, bool):
            var_type = BooleanVar  # variables[name] = BooleanVar(root, value)
        elif isinstance(value, str):
            var_type = StringVar  # variables[name] = StringVar(root, value)

        if var_type is not None:  # type: ignore
            variables[name] = var_type(root, value, name)  # type: ignore
            variables[name].trace("w", update_var)

    # TODO: Fix config file if corrupted ?

    def create_popup_button(
        master: Optional[Misc],
        text: str,
        field: ConfigurationFields,
        minvalue: int,
        maxvalue: int,
        prompt_suffix: str = "",
    ) -> Button:
        if prompt_suffix != "":
            prompt_suffix += "\n"

        def _assign():
            value = simpledialog.askinteger(
                title=f"Asssign '{text}'",
                prompt=f"{prompt_suffix}[{min}-{max}]: ",
                initialvalue=var_get(field),
                minvalue=minvalue,
                maxvalue=maxvalue,
            )
            if value is not None:
                assign(var(field), value)

        return Button(master, text=text, command=_assign)

    hasWebResourceVar = BooleanVar(
        root, (PATH / "resource" / "webResource.json").exists()
    )

    if not get_presets():
        write_save(configuration, False)
        save_preset(configuration, "Default")

    # grouping for enable/disable
    hibernate_group = []
    fill_group = []
    replace_group = []
    mitosis_group = []
    mitosis_cGroup = []
    wallpaper_group = []
    timeout_group = []
    download_group = []
    timer_group = []
    lowkey_group = []
    denial_group = []

    # tab display code start
    tabMaster = ttk.Notebook(root)  # tab manager
    tabGeneral = ttk.Frame(None)  # general tab, will have current configuration
    tabWallpaper = ttk.Frame(None)  # tab for wallpaper rotation configuration
    tabAnnoyance = ttk.Frame(None)  # tab for popup configuration
    tabDrive = ttk.Frame(None)  # tab for drive configuration
    tabJSON = ttk.Frame(None)  # tab for JSON editor (unused)
    tabAdvanced = ttk.Frame(
        None
    )  # advanced tab, will have configuration pertaining to startup, hibernation mode configuration
    tabInfo = ttk.Frame(None)  # info, github, version, about, etc.

    style = ttk.Style(root)  # style setting for left aligned tabs
    style.configure("lefttab.TNotebook", tabposition="wn")
    tabInfoExpound = ttk.Notebook(
        tabInfo, style="lefttab.TNotebook"
    )  # additional subtabs for info on features

    tab_annoyance = ttk.Frame(None)
    tab_drive = ttk.Frame(None)
    tab_wallpaper = ttk.Frame(None)
    tab_launch = ttk.Frame(None)
    tab_hibernate = ttk.Frame(None)
    tab_advanced = ttk.Frame(None)
    tab_thanksAndAbout = ttk.Frame(None)

    tabMaster.add(tabGeneral, text="General")
    # ==========={IN HERE IS GENERAL TAB ITEM INITS}===========#
    # init
    hibernateHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    hibernateFrame = Frame(hibernateHostFrame)
    hibernateMinFrame = Frame(hibernateHostFrame)
    hibernateMaxFrame = Frame(hibernateHostFrame)

    toggleHibernateButton = Checkbutton(
        hibernateHostFrame,
        text="Hibernate Mode",
        variable=var(ConfigurationFields.HIBERNATE_MODE),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.HIBERNATE_MODE), hibernate_group
        ),
    )
    hibernateMinButton = create_popup_button(
        hibernateMinFrame, "Manual min...", ConfigurationFields.HIBERNATE_MIN, 1, 7200
    )

    hibernateMinScale = Scale(
        hibernateMinFrame,
        label="Min Sleep (sec)",
        variable=var(ConfigurationFields.HIBERNATE_MIN),
        orient="horizontal",
        from_=1,
        to=7200,
    )

    hibernateMaxButton = create_popup_button(
        hibernateMaxFrame, "Manual max...", ConfigurationFields.HIBERNATE_MAX, 2, 14400
    )

    hibernateMaxScale = Scale(
        hibernateMaxFrame,
        label="Max Sleep (sec)",
        variable=var(ConfigurationFields.HIBERNATE_MAX),
        orient="horizontal",
        from_=2,
        to=14400,
    )
    h_activityScale = Scale(
        hibernateHostFrame,
        label="Awaken Activity",
        orient="horizontal",
        from_=1,
        to=50,
        variable=var(ConfigurationFields.WAKEUP_ACTIVITY),
    )

    hibernate_group.append(h_activityScale)
    hibernate_group.append(hibernateMinButton)
    hibernate_group.append(hibernateMinScale)
    hibernate_group.append(hibernateMaxButton)
    hibernate_group.append(hibernateMaxScale)

    Label(
        tabGeneral, text="Hibernate configuration", font="Default 13", relief=GROOVE
    ).pack(pady=2)
    hibernateHostFrame.pack(fill="x")
    hibernateFrame.pack(fill="y", side="left")
    toggleHibernateButton.pack(fill="x", side="left", expand=1)
    hibernateMinFrame.pack(fill="y", side="left")
    hibernateMinScale.pack(fill="y")
    hibernateMinButton.pack(fill="y")
    hibernateMaxScale.pack(fill="y")
    hibernateMaxButton.pack(fill="y")
    hibernateMaxFrame.pack(fill="x", side="left")
    h_activityScale.pack(fill="y", side="left")

    # timer configuration
    Label(
        tabGeneral, text="Timer configuration", font="Default 13", relief=GROOVE
    ).pack(pady=2)
    timerFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)

    timerToggle = Checkbutton(
        timerFrame,
        text="Timer Mode",
        variable=var(ConfigurationFields.TIMER_MODE),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.TIMER_MODE), timer_group
        ),
    )
    timerSlider = Scale(
        timerFrame,
        label="Timer Time (mins)",
        from_=1,
        to=1440,
        orient="horizontal",
        variable=var(ConfigurationFields.TIMER_SETUP_TIME),
    )
    safewordFrame = Frame(timerFrame)

    Label(safewordFrame, text="Emergency Safeword").pack()
    timerSafeword = Entry(
        safewordFrame, show="*", textvariable=var(ConfigurationFields.SAFEWORD)
    )
    timerSafeword.pack(expand=1, fill="both")

    timer_group.append(timerSafeword)
    timer_group.append(timerSlider)

    timerToggle.pack(side="left", fill="x", padx=5)
    timerSlider.pack(side="left", fill="x", expand=1, padx=10)
    safewordFrame.pack(side="right", fill="x", padx=5)

    timerFrame.pack(fill="x")

    # mode preset section
    Label(tabGeneral, text="Mode Presets", font="Default 13", relief=GROOVE).pack(
        pady=2
    )
    presetFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    dropdownSelectFrame = Frame(presetFrame)

    style_list = get_presets()
    logging.info(f"pulled style_list={style_list}")
    styleStr = StringVar(root, style_list[0] or "")

    styleDropDown = OptionMenu(
        dropdownSelectFrame,
        styleStr,
        styleStr.get(),
        *style_list,
        command=lambda key: changeDescriptText(key),  # type: ignore : OptionMenu return str not a *Var
    )

    def changeDescriptText(key: str):
        descriptNameLabel.configure(text=f"{key} Description")
        descriptLabel.configure(text=get_preset_description(key))

    def updateHelperFunc(key: str):
        styleStr.set(key)
        changeDescriptText(key)

    def doSave() -> bool:
        name = simpledialog.askstring("Save Preset", "Preset name")
        existed = PATH / "presets" / f"{name}.json"
        if name == None or name == "":
            return False

        write_save(configuration, False)
        if existed:
            if (
                messagebox.askquestion(
                    "Overwrite",
                    "A preset with this name already exists. Overwrite it?",
                )
                == "no"
            ):
                return False

        if save_preset(configuration, name):
            style_list.insert(0, "Default")
            style_list.append(name)
            styleStr.set("Default")
            styleDropDown["menu"].delete(0, "end")
            for item in style_list:
                styleDropDown["menu"].add_command(
                    label=item, command=lambda x=item: updateHelperFunc(x)
                )
            styleStr.set(style_list[0])
        return True

    confirmStyleButton = Button(
        dropdownSelectFrame,
        text="Load Preset",
        command=lambda: apply_preset(configuration, styleStr.get()),
    )
    saveStyleButton = Button(dropdownSelectFrame, text="Save Preset", command=doSave)

    presetDescriptFrame = Frame(presetFrame, borderwidth=2, relief=GROOVE)

    descriptNameLabel = Label(
        presetDescriptFrame, text="Default Description", font="Default 15"
    )
    descriptLabel = Label(
        presetDescriptFrame, text="Default Text Here", relief=GROOVE, wraplength=580
    )
    changeDescriptText("default")

    dropdownSelectFrame.pack(side="left", fill="x", padx=6)
    styleDropDown.pack(fill="x", expand=1)
    confirmStyleButton.pack(fill="both", expand=1)
    Label(dropdownSelectFrame).pack(fill="both", expand=1)
    Label(dropdownSelectFrame).pack(fill="both", expand=1)
    saveStyleButton.pack(fill="both", expand=1)

    presetDescriptFrame.pack(side="right", fill="both", expand=1)
    descriptNameLabel.pack(fill="y", pady=4)
    descriptLabel.pack(fill="both", expand=1)

    presetFrame.pack(fill="both", expand=1)

    # other
    Label(tabGeneral, text="Other", font="Default 13", relief=GROOVE).pack(pady=2)
    otherHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    resourceFrame = Frame(otherHostFrame)
    exportResourcesButton = Button(
        resourceFrame, text="Export resource", command=export_resource_pack
    )
    importResourcesButton = Button(
        resourceFrame, text="Import resources", command=lambda: importResource(root)
    )
    toggleFrame1 = Frame(otherHostFrame)
    toggleFrame2 = Frame(otherHostFrame)

    toggleStartupButton = Checkbutton(
        toggleFrame1,
        text="Launch on Startup",
        variable=var(ConfigurationFields.START_ON_LOGON),
    )
    toggleDiscordButton = Checkbutton(
        toggleFrame1,
        text="Show on Discord",
        variable=var(ConfigurationFields.SHOW_DISCORD),
    )
    toggleFlairButton = Checkbutton(
        toggleFrame2,
        text="Show Loading Flair",
        variable=var(ConfigurationFields.SHOW_LOADING_FLAIR),
    )
    toggleROSButton = Checkbutton(
        toggleFrame2,
        text="Run Edgeware on Save & Exit",
        variable=var(ConfigurationFields.RUN_ON_SAVE_QUIT),
    )

    otherHostFrame.pack(fill="x")
    resourceFrame.pack(fill="y", side="left")
    exportResourcesButton.pack(fill="x")
    importResourcesButton.pack(fill="x")
    toggleFrame1.pack(fill="both", side="left", expand=1)
    toggleStartupButton.pack(fill="x")
    toggleDiscordButton.pack(fill="x")
    toggleFrame2.pack(fill="both", side="left", expand=1)
    toggleFlairButton.pack(fill="x")
    toggleROSButton.pack(fill="x")

    Label(tabGeneral, text="Information", font="Default 13", relief=GROOVE).pack(pady=2)
    infoHostFrame = Frame(tabGeneral, borderwidth=5, relief=RAISED)
    zipGitFrame = Frame(infoHostFrame)
    verFrame = Frame(infoHostFrame)
    # zipDropdown = OptionMenu(tabGeneral, zipDropVar, *DOWNLOAD_STRINGS)
    # zipDownloadButton = Button(tabGeneral, text='Download Zip', command=lambda: downloadZip(zipDropVar.get(), zipLabel))
    zipLabel = Label(
        zipGitFrame,
        text=f"Current Zip:\n{pick_zip()}",
        background="lightgray",
    )
    local_verLabel = Label(verFrame, text=f"Local Version:\n{configuration.version}")
    web_verLabel = Label(
        verFrame,
        text=f"GitHub Version:\n{web_version}",
        bg=(ColorScheme.DEFAULT if (configuration.version == web_version) else "red"),
    )
    openGitButton = Button(
        zipGitFrame,
        text="Open Github",
        command=lambda: webbrowser.open("https://github.com/PetitTournesol/Edgeware"),
    )

    infoHostFrame.pack(fill="x")
    zipGitFrame.pack(fill="both", side="left", expand=1)
    zipLabel.pack(fill="x")
    openGitButton.pack(fill="both", expand=1)
    verFrame.pack(fill="both", side="left", expand=1)
    local_verLabel.pack(fill="x")
    web_verLabel.pack(fill="x")

    optButton = Button(
        infoHostFrame,
        text="Test Func",
        command=lambda: get_preset_description("default"),
    )

    saveExitButton = Button(
        root,
        text="Save & Exit",
        command=lambda: write_save(configuration, True),
    )

    # force reload button for debugging, only appears on DEV versions
    if configuration.version.endswith("DEV"):
        optButton.pack(fill="y", expand=1)

    # zipDownloadButton.grid(column=0, row=10) #not using for now until can find consistent direct download
    # zipDropdown.grid(column=0, row=9)
    # ==========={HERE ENDS  GENERAL TAB ITEM INITS}===========#
    tabMaster.add(tabAnnoyance, text="Annoyance")

    Label(tabAnnoyance).pack()

    delayModeFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)
    delayFrame = Frame(delayModeFrame)
    lowkeyFrame = Frame(delayModeFrame)

    delayScale = Scale(
        delayFrame,
        label="Timer Delay (ms)",
        from_=10,
        to=60000,
        orient="horizontal",
        variable=var(ConfigurationFields.DELAY),
    )
    delayManual = create_popup_button(
        delayModeFrame, "Manual delay...", ConfigurationFields.DELAY, 10, 60000
    )
    opacityScale = Scale(
        tabAnnoyance,
        label="Popup Opacity (%)",
        from_=5,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.LK_SCALING),
    )

    posList = ["Top Right", "Top Left", "Bottom Left", "Bottom Right", "Random"]
    lkItemVar = StringVar(root, posList[var_get(ConfigurationFields.LK_CORNER)])
    lowkeyDropdown = OptionMenu(
        lowkeyFrame,
        lkItemVar,
        *posList,
        command=lambda x: (
            var(ConfigurationFields.LK_CORNER).set(posList.index(x))  # type: ignore : Bad TKinter Typing
        ),
    )
    lowkeyToggle = Checkbutton(
        lowkeyFrame,
        text="Lowkey Mode",
        variable=var(ConfigurationFields.LK_TOGGLE),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.LK_TOGGLE), lowkey_group
        ),
    )

    lowkey_group.append(lowkeyDropdown)

    delayModeFrame.pack(fill="x")

    delayScale.pack(fill="x", expand=1)
    delayManual.pack(fill="x", expand=1)

    delayFrame.pack(side="left", fill="x", expand=1)

    lowkeyFrame.pack(fill="y", side="left")
    lowkeyDropdown.pack(fill="x", padx=2, pady=5)
    lowkeyToggle.pack(fill="both", expand=1)

    opacityScale.pack(fill="x")

    # popup frame handling
    popupHostFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)
    popupFrame = Frame(popupHostFrame)
    timeoutFrame = Frame(popupHostFrame)
    mitosisFrame = Frame(popupHostFrame)
    panicFrame = Frame(popupHostFrame)
    denialFrame = Frame(popupHostFrame)

    popupScale = Scale(
        popupFrame,
        label="Popup Freq (%)",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.POPUP_MOD),
    )
    popupManual = create_popup_button(
        popupFrame, "Manual popup...", ConfigurationFields.POPUP_MOD, 0, 100
    )

    mitosis_group.append(popupScale)
    mitosis_group.append(popupManual)

    def toggleMitosis():
        toggleAssociateconfiguration(
            not var_get(ConfigurationFields.MITOSIS_MODE), mitosis_group
        )
        toggleAssociateconfiguration(
            var_get(ConfigurationFields.MITOSIS_MODE), mitosis_cGroup
        )

    mitosisToggle = Checkbutton(
        mitosisFrame,
        text="Mitosis Mode",
        variable=var(ConfigurationFields.MITOSIS_MODE),
        command=toggleMitosis,
    )
    mitosisStren = Scale(
        mitosisFrame,
        label="Mitosis Strength",
        orient="horizontal",
        from_=2,
        to=10,
        variable=var(ConfigurationFields.MITOSIS_STRENGTH),
    )

    mitosis_cGroup.append(mitosisStren)

    setPanicButtonButton = Button(
        panicFrame,
        text=f"Set Panic Button\n<{var_get(ConfigurationFields.PANIC_BUTTON)}>",
        command=lambda: getKeyboardInput(
            setPanicButtonButton, var(ConfigurationFields.PANIC_BUTTON)
        ),
    )
    doPanicButton = Button(
        panicFrame, text="Perform Panic", command=lambda: utils.run_panic_script()
    )
    panicDisableButton = Checkbutton(
        popupHostFrame,
        text="Disable Panic Hotkey",
        variable=var(ConfigurationFields.PANIC_BUTTON),
    )

    popupWebToggle = Checkbutton(
        popupHostFrame,
        text="Popup close opens web page",
        variable=var(ConfigurationFields.WEB_POPUP),
    )
    toggleCaptionsButton = Checkbutton(
        popupHostFrame,
        text="Popup Captions",
        variable=var(ConfigurationFields.SHOW_CAPTIONS),
    )
    toggleSubliminalButton = Checkbutton(
        popupHostFrame,
        text="Popup Subliminals",
        variable=var(ConfigurationFields.POPUP_SUBLIMINALS),
    )

    timeoutToggle = Checkbutton(
        timeoutFrame,
        text="Popup Timeout",
        variable=var(ConfigurationFields.TIMEOUT_POPUPS),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.TIMEOUT_POPUPS), timeout_group
        ),
    )
    timeoutSlider = Scale(
        timeoutFrame,
        label="Time (sec)",
        from_=1,
        to=120,
        orient="horizontal",
        variable=var(ConfigurationFields.POPUP_TIMEOUT),
    )

    timeout_group.append(timeoutSlider)

    denialSlider = Scale(
        denialFrame,
        label="Denial Chance",
        orient="horizontal",
        variable=var(ConfigurationFields.DENIAL_CHANCE),
    )
    denialToggle = Checkbutton(
        denialFrame,
        text="Denial Mode",
        variable=var(ConfigurationFields.DENIAL_MODE),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.DENIAL_MODE), denial_group
        ),
    )

    denial_group.append(denialSlider)

    popupHostFrame.pack(fill="x")
    popupScale.pack(fill="x")
    popupManual.pack(fill="x")
    popupFrame.pack(fill="y", side="left")
    timeoutSlider.pack(fill="x")
    timeoutToggle.pack(fill="x")
    timeoutFrame.pack(fill="y", side="left")
    mitosisFrame.pack(fill="y", side="left")
    mitosisStren.pack(fill="x")
    mitosisToggle.pack(fill="x")
    denialFrame.pack(fill="y", side="left")
    denialSlider.pack(fill="x")
    denialToggle.pack(fill="x")
    panicFrame.pack(fill="y", side="left")
    setPanicButtonButton.pack(fill="x")
    doPanicButton.pack(fill="x")
    panicDisableButton.pack(fill="x")
    popupWebToggle.pack(fill="x")
    toggleCaptionsButton.pack(fill="x")
    toggleSubliminalButton.pack(fill="x")
    # popup frame handle end

    # other start
    otherHostFrame = Frame(tabAnnoyance, borderwidth=5, relief=RAISED)

    audioFrame = Frame(otherHostFrame)
    webFrame = Frame(otherHostFrame)
    vidFrameL = Frame(otherHostFrame)
    vidFrameR = Frame(otherHostFrame)
    promptFrame = Frame(otherHostFrame)
    mistakeFrame = Frame(otherHostFrame)

    audioScale = Scale(
        audioFrame,
        label="Audio Freq (%)",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.AUDIO_MOD),
    )
    audioManual = create_popup_button(
        audioFrame, "Manual audio...", ConfigurationFields.AUDIO_MOD, 0, 100
    )

    webScale = Scale(
        webFrame,
        label="Website Freq (%)",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.WEB_MOD),
    )
    webManual = create_popup_button(
        webFrame, "Manual web...", ConfigurationFields.WEB_MOD, 0, 100
    )
    vidScale = Scale(
        vidFrameL,
        label="Video Chance (%)",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.VID_MOD),
    )
    vidManual = create_popup_button(
        vidFrameL, "Manual vid...", ConfigurationFields.VID_MOD, 0, 100
    )
    vidVolumeScale = Scale(
        vidFrameR,
        label="Video Volume",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.VIDEO_VOLUME),
    )
    vidVolumeManual = create_popup_button(
        vidFrameR, "Manual volume...", ConfigurationFields.VIDEO_VOLUME, 0, 100
    )

    promptScale = Scale(
        promptFrame,
        label="Prompt Freq (%)",
        from_=0,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.PROMPT_MOD),
    )
    promptManual = create_popup_button(
        promptFrame, "Manual prompt...", ConfigurationFields.PROMPT_MOD, 0, 100
    )

    mistakeScale = Scale(
        mistakeFrame,
        label="Prompt Mistakes",
        from_=0,
        to=150,
        orient="horizontal",
        variable=var(ConfigurationFields.PROMPT_MISTAKES),
    )
    mistakeManual = create_popup_button(
        mistakeFrame,
        "Manual mistakes...",
        ConfigurationFields.PROMPT_MISTAKES,
        0,
        150,
        prompt_suffix="Max mistakes allowed in prompt text",
    )

    otherHostFrame.pack(fill="x")

    audioScale.pack(fill="x", padx=3, expand=1)
    audioManual.pack(fill="x")
    audioFrame.pack(side="left")

    webFrame.pack(fill="y", side="left", padx=3, expand=1)
    webScale.pack(fill="x")
    webManual.pack(fill="x")

    vidFrameL.pack(fill="x", side="left", padx=(3, 0), expand=1)
    vidScale.pack(fill="x")
    vidManual.pack(fill="x")
    vidFrameR.pack(fill="x", side="left", padx=(0, 3), expand=1)
    vidVolumeScale.pack(fill="x")
    vidVolumeManual.pack(fill="x")

    promptFrame.pack(fill="y", side="left", padx=(3, 0), expand=1)
    promptScale.pack(fill="x")
    promptManual.pack(fill="x")
    mistakeFrame.pack(fill="y", side="left", padx=(0, 3), expand=1)
    mistakeScale.pack(fill="x")
    mistakeManual.pack(fill="x")
    # end web
    # ===================={DRIVE}==============================#
    tabMaster.add(tabDrive, text="Drive")

    hardDriveFrame = Frame(tabDrive, borderwidth=5, relief=RAISED)

    pathFrame = Frame(hardDriveFrame)
    fillFrame = Frame(hardDriveFrame)
    replaceFrame = Frame(hardDriveFrame)

    def local_assignPath():
        # nonlocal fillPathVar
        path_ = str(
            filedialog.askdirectory(initialdir="/", title="Select Parent Folder")
        )
        if path_ != "":
            configuration.drivePath = path_
            pathBox.configure(state="normal")
            pathBox.delete(0, 9999)
            pathBox.insert(1, path_)
            pathBox.configure(state="disabled")
            variables["drivePath"].set(pathBox.get())
            configuration.drivePath = pathBox.get()

    pathBox = Entry(pathFrame)
    pathButton = Button(pathFrame, text="Select", command=local_assignPath)

    pathBox.insert(1, configuration.drivePath)
    pathBox.configure(state="disabled")

    fillBox = Checkbutton(
        fillFrame,
        text="Fill Drive",
        variable=var(ConfigurationFields.FILL),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.FILL), fill_group
        ),
    )
    fillDelay = Scale(
        fillFrame,
        label="Fill Delay (10ms)",
        from_=0,
        to=250,
        orient="horizontal",
        variable=var(ConfigurationFields.FILL_DELAY),
    )

    fill_group.append(fillDelay)

    replaceBox = Checkbutton(
        fillFrame,
        text="Replace Images",
        variable=var(ConfigurationFields.REPLACE),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.REPLACE), replace_group
        ),
    )
    replaceThreshScale = Scale(
        fillFrame,
        label="Image Threshold",
        from_=1,
        to=1000,
        orient="horizontal",
        variable=var(ConfigurationFields.REPLACE_THRESH),
    )

    replace_group.append(replaceThreshScale)

    avoidHostFrame = Frame(hardDriveFrame)

    avoidListBox = Listbox(avoidHostFrame, selectmode=SINGLE)
    for name in configuration.avoidList:
        avoidListBox.insert(2, name)
    addName = Button(
        avoidHostFrame,
        text="Add Name",
        command=lambda: add_list(
            configuration,
            avoidListBox,
            "avoidList",
            "Folder Name",
            "Fill/replace will skip any folder with given name.",
        ),
    )
    removeName = Button(
        avoidHostFrame,
        text="Remove Name",
        command=lambda: remove_list(
            configuration,
            avoidListBox,
            "avoidList",
            "Remove EdgeWare",
            "You cannot remove the EdgeWare folder exception.",
        ),
    )
    resetName = Button(
        avoidHostFrame,
        text="Reset",
        command=lambda: reset_list(
            configuration, avoidListBox, "avoidList", "EdgeWare>AppData"
        ),
    )

    avoidHostFrame.pack(fill="y", side="left")
    Label(avoidHostFrame, text="Folder Name Blacklist").pack(fill="x")
    avoidListBox.pack(fill="x")
    addName.pack(fill="x")
    removeName.pack(fill="x")
    resetName.pack(fill="x")

    Label(tabDrive, text="Hard Drive configuration").pack(fill="both")
    hardDriveFrame.pack(fill="x")
    fillFrame.pack(fill="y", side="left")
    fillBox.pack()
    fillDelay.pack()
    replaceFrame.pack(fill="y", side="left")
    replaceBox.pack()
    replaceThreshScale.pack()
    pathFrame.pack(fill="x")
    Label(pathFrame, text="Fill/Replace Start Folder").pack(fill="x")
    pathBox.pack(fill="x")
    pathButton.pack(fill="x")

    downloadHostFrame = Frame(tabDrive, borderwidth=5, relief=RAISED)
    otherFrame = Frame(downloadHostFrame)
    tagFrame = Frame(downloadHostFrame)
    booruFrame = Frame(downloadHostFrame)
    booruNameEntry = Entry(booruFrame, textvariable=var(ConfigurationFields.BOORU_NAME))
    downloadEnabled = Checkbutton(
        otherFrame,
        text="Download from Booru",
        variable=var(ConfigurationFields.DOWNLOAD_ENABLED),
        command=lambda: (
            toggleAssociateconfiguration_manual(
                var_get(ConfigurationFields.DOWNLOAD_ENABLED),
                download_group,
                "white",
                "gray25",
            )
        ),
    )
    downloadResourceEnabled = Checkbutton(
        otherFrame,
        text="Download from webResource",
        variable=var(ConfigurationFields.USE_WEB_RESOURCE),
    )
    toggleAssociateconfiguration(hasWebResourceVar.get(), [downloadResourceEnabled])
    downloadMode = OptionMenu(
        booruFrame,
        var(ConfigurationFields.DOWNLOAD_MODE),
        *["All", "First Page", "Random Page"],
    )
    downloadMode.configure(width=15)
    minScoreSlider = Scale(
        booruFrame,
        from_=-50,
        to=100,
        orient="horizontal",
        variable=var(ConfigurationFields.BOORU_MIN_SCORE),
        label="Minimum Score",
    )

    booruValidate = Button(
        booruFrame,
        text="Validate",
        command=lambda: (
            messagebox.showinfo("Success!", "Booru is valid.")
            if validateBooru(var_get(ConfigurationFields.BOORU_NAME))
            else messagebox.showerror("Failed", "Booru is invalid.")
        ),
    )

    tagListBox = Listbox(tagFrame, selectmode=SINGLE)
    for tag in configuration.tagList:
        tagListBox.insert(1, tag)
    addTag = Button(
        tagFrame,
        text="Add Tag",
        command=lambda: add_list(
            configuration, tagListBox, "tagList", "New Tag", "Enter Tag(s)"
        ),
    )
    removeTag = Button(
        tagFrame,
        text="Remove Tag",
        command=lambda: remove_list(
            configuration,
            tagListBox,
            "tagList",
            "Remove Failed",
            'Cannot remove all tags. To download without a tag, use "all" as the tag.',
        ),
    )
    resetTag = Button(
        tagFrame,
        text="Reset Tags",
        command=lambda: reset_list(configuration, tagListBox, "tagList", "all"),
    )

    download_group.append(booruNameEntry)
    download_group.append(booruValidate)
    download_group.append(tagListBox)
    download_group.append(addTag)
    download_group.append(removeTag)
    download_group.append(resetTag)
    download_group.append(downloadMode)
    download_group.append(minScoreSlider)

    Label(tabDrive, text="Image Download configuration").pack(fill="x")
    Label(
        downloadHostFrame,
        text="THE BOORU DOWNLOADER IS OUTDATED AND BROKEN. IT WILL LIKELY BARELY FUNCTION, IF AT ALL.\nNo I will not fix it, this shit is a pain in the ass and I'm stupid.",
        foreground="red",
    ).pack(fill="x")
    tagFrame.pack(fill="y", side="left")
    booruFrame.pack(fill="y", side="left")
    otherFrame.pack(fill="both", side="right")

    downloadEnabled.pack()
    downloadHostFrame.pack(fill="both")
    tagListBox.pack(fill="x")
    addTag.pack(fill="x")
    removeTag.pack(fill="x")
    resetTag.pack(fill="x")
    Label(booruFrame, text="Booru Name").pack(fill="x")
    booruNameEntry.pack(fill="x")
    booruValidate.pack(fill="x")
    Label(booruFrame, text="Download Mode").pack(fill="x")
    downloadMode.pack(fill="x")
    minScoreSlider.pack(fill="x")
    downloadResourceEnabled.pack(fill="x")

    tabMaster.add(tabWallpaper, text="Wallpaper")
    # ==========={WALLPAPER TAB ITEMS} ========================#
    rotateCheckbox = Checkbutton(
        tabWallpaper,
        text="Rotate Wallpapers",
        variable=var(ConfigurationFields.ROTATE_WALLPAPER),
        command=lambda: toggleAssociateconfiguration(
            var_get(ConfigurationFields.ROTATE_WALLPAPER), wallpaper_group
        ),
    )
    wpList = Listbox(tabWallpaper, selectmode=SINGLE)
    for key in configuration.wallpaperDat:
        wpList.insert(1, key)
    addWPButton = Button(
        tabWallpaper,
        text="Add/Edit Wallpaper",
        command=lambda: add_wallpaper(configuration, wpList),
    )
    remWPButton = Button(
        tabWallpaper,
        text="Remove Wallpaper",
        command=lambda: removeWallpaper(configuration, wpList),
    )
    autoImport = Button(
        tabWallpaper,
        text="Auto Import",
        command=lambda: autoImportWallpapers(configuration, wpList),
    )
    varSlider = Scale(
        tabWallpaper,
        orient="horizontal",
        label="Rotate Variation (sec)",
        from_=0,
        to=(var_get(ConfigurationFields.ROTATE_WALLPAPER) - 1),
        variable=var(ConfigurationFields.WALLPAPER_VARIANCE),
    )
    wpDelaySlider = Scale(
        tabWallpaper,
        orient="horizontal",
        label="Rotate Timer (sec)",
        from_=5,
        to=300,
        variable=var(ConfigurationFields.WALLPAPER_TIMER),
        command=lambda val: update_max(varSlider, int(val) - 1),
    )

    pHoldImageR = Image.open(
        os.path.join(PATH, "default_assets", "default_win10.jpg")
    ).resize(
        (int(root.winfo_screenwidth() * 0.13), int(root.winfo_screenheight() * 0.13)),
        Image.Resampling.NEAREST,
    )

    def updatePanicPaper():
        nonlocal pHoldImageR
        selectedFile = filedialog.askopenfile(
            "rb", filetypes=[("image file", ".jpg .jpeg .png")]
        )
        if not isinstance(selectedFile, type(None)):
            try:
                img = Image.open(selectedFile.name).convert("RGB")
                img.save(os.path.join(PATH, "default_assets", "default_win10.jpg"))
                pHoldImageR = ImageTk.PhotoImage(
                    img.resize(
                        (
                            int(root.winfo_screenwidth() * 0.13),
                            int(root.winfo_screenheight() * 0.13),
                        ),
                        Image.Resampling.NEAREST,
                    )
                )
                panicWallpaperLabel.config(image=pHoldImageR)  # type: ignore # FIXME ?
                panicWallpaperLabel.update_idletasks()
            except Exception as e:
                logging.warning(f"failed to open/change default wallpaper\n{e}")

    panicWPFrame = Frame(tabWallpaper)
    panicWPFrameL = Frame(panicWPFrame)
    panicWPFrameR = Frame(panicWPFrame)
    panicWallpaperImage = ImageTk.PhotoImage(pHoldImageR)
    panicWallpaperButton = Button(
        panicWPFrameL, text="Change Panic Wallpaper", command=updatePanicPaper
    )
    panicWallpaperLabel = Label(
        panicWPFrameR, text="Current Panic Wallpaper", image=panicWallpaperImage  # type: ignore # FIXME ?
    )

    wallpaper_group.append(wpList)
    wallpaper_group.append(addWPButton)
    wallpaper_group.append(remWPButton)
    wallpaper_group.append(wpDelaySlider)
    wallpaper_group.append(autoImport)
    wallpaper_group.append(varSlider)

    rotateCheckbox.pack(fill="x")
    wpList.pack(fill="x")
    addWPButton.pack(fill="x")
    remWPButton.pack(fill="x")
    autoImport.pack(fill="x")
    wpDelaySlider.pack(fill="x")
    varSlider.pack(fill="x")
    panicWPFrame.pack(fill="x", expand=1)
    panicWPFrameL.pack(side="left", fill="y")
    panicWPFrameR.pack(side="right", fill="x", expand=1)
    panicWallpaperButton.pack(fill="x", padx=5, pady=5, expand=1)
    Label(panicWPFrameR, text="Current Panic Wallpaper").pack(fill="x")
    panicWallpaperLabel.pack()
    tabMaster.add(tabAdvanced, text="Advanced")
    # ==========={IN HERE IS ADVANCED TAB ITEM INITS}===========#
    itemList = []
    for settingName in configuration.as_dict().keys():
        itemList.append(settingName)
    dropdownObj = StringVar(root, itemList[0])
    textObj = StringVar(root, configuration[dropdownObj.get()])
    advPanel = Frame(tabAdvanced)
    textInput = Entry(advPanel)
    textInput.insert(1, textObj.get())
    expectedLabel = Label(
        tabAdvanced, text=f"Expected value: {DEFAULT_CONFIGURATION[dropdownObj.get()]}"
    )
    dropdownMenu = OptionMenu(
        advPanel,
        dropdownObj,
        *itemList,
        command=lambda a: update_texts(
            [textInput, expectedLabel], configuration[a.get()], a.get()
        ),
    )
    dropdownMenu.configure(width=10)
    applyButton = Button(
        advPanel,
        text="Apply",
        command=lambda: assignJSON(configuration, dropdownObj.get(), textInput.get()),
    )
    Label(tabAdvanced).pack()
    Label(
        tabAdvanced,
        text="Be careful messing with some of these; improper configuring can cause\nproblems when running, or potentially cause unintended damage to files.",
    ).pack()
    Label(tabAdvanced).pack()
    Label(tabAdvanced).pack()
    advPanel.pack(fill="x", padx=2)
    dropdownMenu.pack(padx=2, side="left")
    textInput.pack(padx=2, fill="x", expand=1, side="left")
    applyButton.pack(padx=2, fill="x", side="right")
    expectedLabel.pack()
    # ==========={HERE ENDS  ADVANCED TAB ITEM INITS}===========#
    tabMaster.add(tabInfo, text="About")
    # ==========={IN HERE IS ABOUT TAB ITEM INITS}===========#
    tabInfoExpound.add(tab_annoyance, text="Annoyance")
    Label(tab_annoyance, text=ANNOYANCE_TEXT, anchor="nw", wraplength=460).pack()
    tabInfoExpound.add(tab_drive, text="Hard Drive")
    Label(tab_drive, text=DRIVE_TEXT, anchor="nw", wraplength=460).pack()
    # tabInfoExpound.add(tab_export, text='Exporting')
    tabInfoExpound.add(tab_wallpaper, text="Wallpaper")
    Label(tab_wallpaper, text=WALLPAPER_TEXT, anchor="nw", wraplength=460).pack()
    tabInfoExpound.add(tab_launch, text="Startup")
    Label(tab_launch, text=STARTUP_TEXT, anchor="nw", wraplength=460).pack()
    tabInfoExpound.add(tab_hibernate, text="Hibernate")
    Label(tab_hibernate, text=HIBERNATE_TEXT, anchor="nw", wraplength=460).pack()
    tabInfoExpound.add(tab_advanced, text="Advanced")
    Label(tab_advanced, text=ADVANCED_TEXT, anchor="nw", wraplength=460).pack()
    tabInfoExpound.add(tab_thanksAndAbout, text="Thanks & About")
    Label(
        tab_thanksAndAbout, text=THANK_AND_ABOUT_TEXT, anchor="nw", wraplength=460
    ).pack()
    # ==========={HERE ENDS  ABOUT TAB ITEM INITS}===========#

    toggleAssociateconfiguration(configuration.fill, fill_group)
    toggleAssociateconfiguration(configuration.replace, replace_group)
    toggleAssociateconfiguration(configuration.hibernateMode, hibernate_group)
    toggleAssociateconfiguration(configuration.rotateWallpaper, wallpaper_group)
    toggleAssociateconfiguration(configuration.timeoutPopups, timeout_group)
    toggleAssociateconfiguration(configuration.mitosisMode, mitosis_cGroup)
    toggleAssociateconfiguration(not configuration.mitosisMode, mitosis_group)
    toggleAssociateconfiguration_manual(
        var_get(ConfigurationFields.DOWNLOAD_ENABLED), download_group, "white", "gray25"
    )
    toggleAssociateconfiguration(configuration.timerMode, timer_group)
    toggleAssociateconfiguration(configuration.lkToggle, lowkey_group)
    toggleAssociateconfiguration(configuration.denialMode, denial_group)

    tabMaster.pack(expand=1, fill="both")
    tabInfoExpound.pack(expand=1, fill="both")
    saveExitButton.pack(fill="x")

    timeObjPath = PATH / "hid_time.dat"

    utils.expose_file(timeObjPath)
    if timeObjPath.exists():
        time_ = int(timeObjPath.read_text()) / 60
        if not time_ == int(configuration.timerSetupTime):
            timerToggle.configure(state=DISABLED)
            for item in timer_group:
                item.configure(state=DISABLED)
    utils.hide_file(timeObjPath)

    # first time alert popup
    # if not configuration['is_configed'] == 1:
    #    messagebox.showinfo('First Config', 'Config has not been run before. All configuration are defaulted to frequency of 0 except for popups.\n[This alert will only appear on the first run of config]')
    # version alert, if core web version (0.0.0) is different from the github configdefault, alerts user that update is available
    #   if user is a bugfix patch behind, the _X at the end of the 0.0.0, they will not be alerted
    #   the version will still be red to draw attention to it
    if configuration.version.split("_")[0] != web_version.split("_")[
        0
    ] and not configuration.version.endswith("DEV"):
        messagebox.showwarning(
            "Update Available",
            "Main local version and web version are not the same.\nPlease visit the Github and download the newer files.",
        )
    root.mainloop()

    return configuration


def pick_zip() -> Optional[str]:
    # Selecting zip
    for obj in PATH.glob("*.zip"):
        logging.info(f"Found zip file {obj}")
        return obj.name


def export_resource_pack() -> bool:
    try:
        logging.info("Starting zip export...")
        save_location = filedialog.asksaveasfile("w", defaultextension=".zip")
        if save_location is None:
            return False

        with zipfile.ZipFile(
            save_location.name, "w", compression=zipfile.ZIP_DEFLATED
        ) as zip:
            beyond_root = False
            for root, dirs, files in os.walk(PATH / "resource"):
                root = Path(root)
                for file in files:
                    source = (root / file).absolute()
                    destination = root.relative_to(PATH) / file if beyond_root else file
                    logging.info(f"Writing {source} into {destination}")
                    zip.write(source, destination)

                for dir in dirs:
                    logging.info(f"Making dir {dir}")
                    zip.write((root / dir).absolute(), dir)
                beyond_root = True
        return True
    except Exception as e:
        logging.fatal(f"Failed to export zip\n\tReason: {e}")
        messagebox.showerror("Write Error", "Failed to export resource to zip file.")
        return False


def importResource(parent: Tk) -> bool:
    try:
        openLocation = filedialog.askopenfile("r", defaultextension=".zip")
        if openLocation == None:
            return False
        if (PATH / "resource").exists():
            resp = confirmBox(
                parent,
                "Current resource folder will be deleted and overwritten. Is this okay?",
            )
            if not resp:
                logging.info("exited import resource overwrite")
                return False
            shutil.rmtree(PATH / "resource")
            logging.info("removed old resource folder")
        with zipfile.ZipFile(openLocation.name, "r") as zip:
            zip.extractall(PATH / "resource")
            logging.info("extracted all from zip")
        messagebox.showinfo("Done", "Resource importing completed.")
        return True
    except Exception as e:
        messagebox.showerror(
            "Read Error", f"Failed to import resources from file.\n[{e}]"
        )
        return False


def confirmBox(parent: Tk, message: str) -> bool:
    allow = False
    root = Toplevel(parent)

    def complete(state: bool):
        nonlocal allow
        allow = state
        root.quit()

    root.geometry("220x120")
    root.resizable(False, False)
    if utils.is_windows():
        root.wm_attributes("-toolwindow", 1)
    root.focus_force()
    root.title("Confirm")
    Label(root, text=message, wraplength=212).pack(fill="x")
    # Label(root).pack()
    Button(root, text="Continue", command=lambda: complete(True)).pack()
    Button(root, text="Cancel", command=lambda: complete(False)).pack()
    root.mainloop()
    try:
        root.destroy()
    except:
        pass
    return allow


# helper funcs for lambdas =======================================================


def write_save(configuration: Configuration, exit_at_end: bool):
    logging.info("starting config save write...")
    temp = json.loads("{}")
    configuration.is_configured = True
    # TODO: Check if replacement is ok:
    # config_file.write_text(json.dumps(configuration))
    configuration.save()

    utils.toggle_run_at_startup(PATH, configuration.start_on_logon)

    SHOWN_ATTR = 0x08
    HIDDEN_ATTR = 0x02
    hash_obj_path = PATH / "pass.hash"
    time_obj_path = PATH / "hid_time.dat"

    if configuration.timerMode:
        utils.toggle_run_at_startup(PATH, True)

        # revealing hidden files
        utils.expose_file(hash_obj_path)
        utils.expose_file(time_obj_path)
        logging.info("Revealed hashed pass and time files")

        with open(hash_obj_path, "w") as passFile, open(time_obj_path, "w") as timeFile:
            logging.info("Attempting file writes...")
            passFile.write(
                hashlib.sha256(
                    configuration.safeword.encode(encoding="ascii", errors="ignore")
                ).hexdigest()
            )
            timeFile.write(str(configuration.timerSetupTime * 60))
            logging.info("Wrote files.")

        # hiding hash file with saved password hash for panic and time data
        utils.hide_file(hash_obj_path)
        utils.hide_file(time_obj_path)
        logging.info("Hid hashed pass and time files")
    else:
        try:
            if not configuration.start_on_logon:
                utils.toggle_run_at_startup(PATH, False)
            utils.expose_file(hash_obj_path)
            utils.expose_file(time_obj_path)
            os.remove(hash_obj_path)
            os.remove(time_obj_path)
            logging.info("Removed pass/time files.")
        except Exception as e:
            errText = (
                str(e)
                .lower()
                .replace(
                    getpass.getuser(),
                    "[USERnameREDACTED]",
                )
            )
            logging.warning(f"Failed timer file modifying\n\tReason: {errText}")
            pass

    configuration.save()
    logging.info(f"wrote config file: {json.dumps(configuration.as_dict())}")

    if configuration.runOnSaveQuit and exit_at_end:
        utils.run_script("start.py")

    if exit_at_end:
        logging.info("Exiting config")
        os.kill(os.getpid(), 9)


def validateBooru(name: str) -> bool:
    return requests.get(BOORU_URL.replace(BOORU_FLAG, name)).status_code == 200


def get_live_version() -> str:
    try:
        logging.info("fetching github version")
        with open(urllib.request.urlretrieve(UPDCHECK_URL)[0], "r") as liveDCfg:
            return liveDCfg.read().split("\n")[1].split(",")[0]
    except Exception as e:
        logging.warning("failed to fetch github version.\n\tReason: {e}")
        return "Could not check version."


def add_list(
    configuration: Configuration, listbox: Listbox, key: str, title: str, text: str
):
    name = simpledialog.askstring(title, text)
    if name != "" and name != None:
        configuration[key].append(name)
        listbox.insert(listbox.size() + 1, name)


def remove_list(
    configuration: Configuration, listbox: Listbox, key: str, title: str, text: str
):
    index = int(listbox.curselection()[0])
    if index > 0:
        listbox.delete(first=listbox.curselection())
        elments: list = configuration[key]
        del elments[index]
    else:
        messagebox.showwarning(title, text)


def reset_list(configuration: Configuration, listbox: Listbox, key: str, default):
    try:
        listbox.delete(0, listbox.size())
    except Exception as e:
        print(e)

    configuration[key] = default
    for i, item in enumerate(configuration[key], 1):
        listbox.insert(i, item)


def add_wallpaper(configuration: Configuration, listbox: Listbox):
    file = filedialog.askopenfile("r", filetypes=[("image file", ".jpg .jpeg .png")])
    if not isinstance(file, type(None)):
        lname = simpledialog.askstring(
            "Wallpaper Name", "Wallpaper Label\n(Name displayed in list)"
        )
        if not isinstance(lname, type(None)):
            print(file.name.split("/")[-1])
            configuration.wallpaperDat[lname] = file.name.split("/")[-1]
            listbox.insert(1, lname)


def removeWallpaper(configuration: Configuration, listbox: Listbox):
    index = int(listbox.curselection()[0])
    item_name = listbox.get(index)
    if index > 0:
        del configuration.wallpaperDat[item_name]
        listbox.delete(first=listbox.curselection())
    else:
        messagebox.showwarning(
            "Remove Default", "You cannot remove the default wallpaper."
        )


def autoImportWallpapers(configuration: Configuration, listbox: Listbox):
    allow_ = confirmBox(
        listbox.winfo_toplevel(),  # type: ignore # FIXME
        "Current list will be cleared before new list is imported from the /resource folder. Is that okay?",
    )
    if allow_:
        # Clear list
        configuration.wallpaperDat.clear()
        listbox.delete(1, listbox.size())

        for file in os.listdir(os.path.join(PATH, "resource")):
            if (
                file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")
            ) and file != "wallpaper.png":
                name = file.split(".")[0]
                listbox.insert(1, name)
                configuration.wallpaperDat[name] = file


def update_max(obj, value: int):
    obj.configure(value)


def update_texts(objs: List[Union[Entry, Label]], var: str, var_Label: str):
    for obj in objs:
        if isinstance(obj, Entry):
            obj.delete(0, 9999)
            obj.insert(1, var)
        elif isinstance(obj, Label):
            obj.configure(text=f"Expected value: {DEFAULT_CONFIGURATION[var_Label]}")


def update_text(obj: Union[Entry, Label], var: str, var_Label: str):
    try:
        if isinstance(obj, Entry):
            obj.delete(0, 9999)
            obj.insert(1, var)
        elif isinstance(obj, Label):
            obj.configure(text=f"Expected value: {DEFAULT_CONFIGURATION[var_Label]}")
    except:
        print("idk what would cause this but just in case uwu")


def assignJSON(configuration: Configuration, key: str, var: Union[int, str]):
    configuration[key] = var
    configuration.save()


def toggleAssociateconfiguration(ownerState: bool, objList: list):
    toggleAssociateconfiguration_manual(
        ownerState, objList, ColorScheme.DEFAULT, "gray25"
    )


def toggleAssociateconfiguration_manual(
    ownerState: bool, objList: list, colorOn: Union[int, str], colorOff: Union[int, str]
):
    logging.info(f"toggling state of {objList} to {ownerState}")
    for tkObject in objList:
        tkObject.configure(state=("normal" if ownerState else "disabled"))
        tkObject.configure(bg=(colorOn if ownerState else colorOff))


def assign(obj: Union[StringVar, IntVar, BooleanVar], var: Union[str, int, bool]):
    try:
        obj.set(var)  # type: ignore # FIXME
    except Exception as e:
        raise e
        """"""
        # no assignment


def getKeyboardInput(button: Button, var: StringVar):
    child = Tk()
    child.resizable(False, False)
    child.title("Key Listener")
    child.wm_attributes("-topmost", 1)
    child.geometry("250x250")
    child.focus_force()
    Label(child, text="Press any key or exit").pack(expand=1, fill="both")
    child.bind("<KeyPress>", lambda key: assignKey(child, button, var, key))
    child.mainloop()


def assignKey(parent: Tk, button: Button, var: StringVar, key):
    button.configure(text=f"Set Panic Button\n<{key.keysym}>")
    var.set(str(key.keysym))
    parent.destroy()


def get_presets() -> List[str]:
    presets_folder = PATH / "presets"
    presets_folder.mkdir(exist_ok=True, parents=True)
    return [file.name[:-5] for file in presets_folder.glob("*.json")]


def apply_preset(configuration: Configuration, name: str):
    preset_path = PATH / "presets" / f"{name}.json"
    try:
        preset = Configuration.load(
            str(preset_path.resolve().absolute()), panic_on_error=True
        )
        preset.save()  # type: ignore because we raise error if it fails
    except ValidationError as e:
        messagebox.showerror(
            "Failed to load preset",
            f"The preset files seems to be corrupted\nMore info the logs",
        )
    except Exception as e:
        messagebox.showerror(
            "Failed to load preset",
            f"Couldn't find the preset file\nMore info the logs",
        )


def save_preset(configuration: Configuration, name: str) -> bool:
    try:
        preset_destination = PATH / "presets" / f"{name}.json"
        configuration.save(str(preset_destination.resolve().absolute()))
    except Exception as e:
        logging.error(e)
        return False
    return True


def get_preset_description(name: str) -> str:
    try:
        preset_path = PATH / "presets" / f"{name}.txt"
        return preset_path.read_text()
    except FileNotFoundError as e:
        return "Couldn't find the preset description"
    except Exception as e:
        logging.error(e)
        return "An error occured please check the logs"


if __name__ == "__main__":
    try:
        configuration = open_configuration()
        configuration.save()
    except Exception as e:
        logging.fatal(f"Config encountered fatal error:\n{e}")
        messagebox.showerror("Could not start", f"Could not start config.\n[{e}]")
