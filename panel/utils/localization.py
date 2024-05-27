from simple_enum import SimpleEnum

class LANG_ENUM(SimpleEnum):
    ZH_CN = None
    EN_US = None


class LANG_STR_ENUM(SimpleEnum):
    UI_APP_TITLE = None
    ERROR_HOU_PATH = None
    ERROR_HOU_PATH_SETTINGS = None
    ERROR_PYLIB_PATH = None
    UI_MENU_FILE = None
    UI_MENU_FILE_OPEN_HDA = None
    UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE = None
    UI_MENU_FILE_OPEN_HIP = None
    UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE = None
    UI_MENU_FILE_OPEN_RECENT = None
    UI_MENU_SETTINGS = None
    UI_MENU_SETTINGS_SAVE = None
    UI_MENU_SETTINGS_GENERAL = None
    UI_MENU_SETTINGS_HOUDINI_ROOT = None
    UI_MENU_SETTINGS_LANGUAGE = None
    UI_MENU_SETTINGS_LANGUAGE_EN_US = None
    UI_MENU_SETTINGS_LANGUAGE_ZH_CN = None
    UI_HDAPANEL_EMPTY_HDA = None


LANG_MAP = {LANG_STR_ENUM.ERROR_HOU_PATH: {LANG_ENUM.EN_US: "Houdini path not exist.", LANG_ENUM.ZH_CN: "Houdini路径不存在"},
            LANG_STR_ENUM.ERROR_HOU_PATH_SETTINGS: {LANG_ENUM.EN_US: "Houdini path not exist, please click Settings>General Settings to set.", LANG_ENUM.ZH_CN: "Houdini路径不存在，请点击设置>常规设置进行设置"},
            LANG_STR_ENUM.UI_APP_TITLE: {LANG_ENUM.EN_US: "Portable Houdini", LANG_ENUM.ZH_CN: "Portable Houdini"},
            LANG_STR_ENUM.ERROR_PYLIB_PATH: {LANG_ENUM.EN_US: "Houdini pylib path not exist.", LANG_ENUM.ZH_CN: "Houdini Pylib路径不存在"},
            LANG_STR_ENUM.UI_MENU_FILE: {LANG_ENUM.EN_US: "File", LANG_ENUM.ZH_CN: "文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA: {LANG_ENUM.EN_US: "Open HDA", LANG_ENUM.ZH_CN: "打开HDA"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE: {LANG_ENUM.EN_US: "Open HDA File", LANG_ENUM.ZH_CN: "打开HDA文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP: {LANG_ENUM.EN_US: "Open HIP", LANG_ENUM.ZH_CN: "打开HIP"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE: {LANG_ENUM.EN_US: "Open HIP File", LANG_ENUM.ZH_CN: "打开HIP文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_RECENT: {LANG_ENUM.EN_US: "Open Recent File", LANG_ENUM.ZH_CN: "打开最近文件"},
            LANG_STR_ENUM.UI_MENU_SETTINGS: {LANG_ENUM.EN_US: "Settings", LANG_ENUM.ZH_CN: "设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_SAVE: {LANG_ENUM.EN_US: "Save Settings", LANG_ENUM.ZH_CN: "保存设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_GENERAL: {LANG_ENUM.EN_US: "General Settings", LANG_ENUM.ZH_CN: "常规设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_HOUDINI_ROOT: {LANG_ENUM.EN_US: "Houdini Root", LANG_ENUM.ZH_CN: "Houdini根目录"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE: {LANG_ENUM.EN_US: "Language", LANG_ENUM.ZH_CN: "语言"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_EN_US: {LANG_ENUM.EN_US: "English", LANG_ENUM.ZH_CN: "英文"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_ZH_CN: {LANG_ENUM.EN_US: "Chinese", LANG_ENUM.ZH_CN: "中文"},
            LANG_STR_ENUM.UI_HDAPANEL_EMPTY_HDA: {LANG_ENUM.EN_US: "Select a HDA", LANG_ENUM.ZH_CN: "打开一个HDA"},
            }


def getLocalizationStr(str_enum, lang_enum=None):
    if lang_enum is None:
        from globals import LANGUAGE
        lang_enum = LANGUAGE

    if LANG_MAP.__contains__(str_enum):
        if LANG_MAP[str_enum].__contains__(lang_enum):
            return LANG_MAP[str_enum][lang_enum]

    return ""
