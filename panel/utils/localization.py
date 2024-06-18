from simple_enum import SimpleEnum

class LANG_ENUM(SimpleEnum):
    ZH_CN = None
    EN_US = None


class LANG_STR_ENUM(SimpleEnum):
    UI_APPLY = None
    UI_CANCEL = None
    UI_WARNING = None
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
    UI_TWIRL_EXPANSION_DESCRIPTION = None
    UI_TWIRL_COLLAPSE_DESCRIPTION = None
    UI_HDAPANEL_EMPTY_HDA = None
    UI_HDAPANEL_AUTO_RECOOK = None
    UI_HDAPANEL_FORCE_RECOOK = None
    UI_HDAPANEL_BATCH_LABEL = None
    UI_HDAPANEL_BATCH_BUTTON = None
    UI_BATCHPANEL_TITLE = None
    UI_BATCHPANEL_INDEX = None
    UI_BATCHPANEL_VALUE = None
    UI_BATCHPANEL_CLEAR = None
    UI_BATCHPANEL_IMPORT = None
    UI_BATCHPANEL_INHERIT = None
    UI_BATCHPANEL_SELECT_REMOVE_ROW = None
    UI_BATCHPANEL_BUTTON_TOOLTIP = None


LANG_MAP = {LANG_STR_ENUM.UI_APPLY: {LANG_ENUM.EN_US: "Apply", LANG_ENUM.ZH_CN: "应用"},
            LANG_STR_ENUM.UI_CANCEL: {LANG_ENUM.EN_US: "Cancel", LANG_ENUM.ZH_CN: "取消"},
            LANG_STR_ENUM.UI_WARNING: {LANG_ENUM.EN_US: "Warning", LANG_ENUM.ZH_CN: "警告"},
            LANG_STR_ENUM.ERROR_HOU_PATH: {LANG_ENUM.EN_US: "Houdini path not exist.", LANG_ENUM.ZH_CN: "Houdini路径不存在"},
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
            LANG_STR_ENUM.UI_HDAPANEL_AUTO_RECOOK: {LANG_ENUM.EN_US: "Auto Recook", LANG_ENUM.ZH_CN: "自动计算"},
            LANG_STR_ENUM.UI_HDAPANEL_FORCE_RECOOK: {LANG_ENUM.EN_US: "Force Recook", LANG_ENUM.ZH_CN: "强制重新计算"},
            LANG_STR_ENUM.UI_HDAPANEL_BATCH_LABEL: {LANG_ENUM.EN_US: "Batches: ", LANG_ENUM.ZH_CN: "批处理数: "},
            LANG_STR_ENUM.UI_HDAPANEL_BATCH_BUTTON: {LANG_ENUM.EN_US: "Batching", LANG_ENUM.ZH_CN: "批处理"},
            LANG_STR_ENUM.UI_TWIRL_EXPANSION_DESCRIPTION: {LANG_ENUM.EN_US: "⇓Click to Expand Batching/Recook settings⇓", LANG_ENUM.ZH_CN: "⇓点击展开批处理/重计算设置⇓"},
            LANG_STR_ENUM.UI_TWIRL_COLLAPSE_DESCRIPTION: {LANG_ENUM.EN_US: "⇑Click to Collapse Batching/Recook settings⇑", LANG_ENUM.ZH_CN: "⇑点击收起批处理/重计算设置⇑"},
            LANG_STR_ENUM.UI_BATCHPANEL_TITLE: {LANG_ENUM.EN_US: "Batch", LANG_ENUM.ZH_CN: "批处理"},
            LANG_STR_ENUM.UI_BATCHPANEL_INDEX: {LANG_ENUM.EN_US: "Batch Index", LANG_ENUM.ZH_CN: "批次"},
            LANG_STR_ENUM.UI_BATCHPANEL_VALUE: {LANG_ENUM.EN_US: "Value", LANG_ENUM.ZH_CN: "属性值"},
            LANG_STR_ENUM.UI_BATCHPANEL_CLEAR: {LANG_ENUM.EN_US: "Clear", LANG_ENUM.ZH_CN: "清空"},
            LANG_STR_ENUM.UI_BATCHPANEL_IMPORT: {LANG_ENUM.EN_US: "Import", LANG_ENUM.ZH_CN: "导入"},
            LANG_STR_ENUM.UI_BATCHPANEL_INHERIT: {LANG_ENUM.EN_US: "--Inherit Last Row--", LANG_ENUM.ZH_CN: "--继承上行参数--"},
            LANG_STR_ENUM.UI_BATCHPANEL_SELECT_REMOVE_ROW: {LANG_ENUM.EN_US: "Select the row to delete", LANG_ENUM.ZH_CN: "选择需要删除的项"},
            LANG_STR_ENUM.UI_BATCHPANEL_BUTTON_TOOLTIP: {LANG_ENUM.EN_US: "Selected indicates that a click event will be triggered", LANG_ENUM.ZH_CN: "选中表示会触发点击事件"},
            }


def getLocalizationStr(str_enum, lang_enum=None):
    if lang_enum is None:
        from globals import LANGUAGE
        lang_enum = LANGUAGE

    if LANG_MAP.__contains__(str_enum):
        if LANG_MAP[str_enum].__contains__(lang_enum):
            return LANG_MAP[str_enum][lang_enum]

    return ""
