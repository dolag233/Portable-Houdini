from simple_enum import SimpleEnum
from panel.utils.language_enum import LANG_ENUM


class LANG_STR_ENUM(SimpleEnum):
    UI_APPLY = None
    UI_CANCEL = None
    UI_WARNING = None
    UI_APP_TITLE = None
    ERROR_HOU_PATH = None
    ERROR_HOU_PATH_SETTINGS = None
    ERROR_PYLIB_PATH = None
    ERROR_TITLE = None
    ERROR_INVALID_FILE_PATH = None
    UI_MENU_FILE = None
    UI_MENU_FILE_OPEN_HDA = None
    UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE = None
    UI_MENU_FILE_OPEN_HIP = None
    UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE = None
    UI_MENU_FILE_OPEN_RECENT = None
    UI_MENU_FILE_SAVE_HIP = None
    UI_MENU_FILE_SAVE_HIP_FILE_DIALOG_TITLE = None
    UI_MENU_SETTINGS = None
    UI_MENU_SETTINGS_SAVE = None
    UI_MENU_SETTINGS_GENERAL = None
    UI_MENU_SETTINGS_HOUDINI_ROOT = None
    UI_MENU_SETTINGS_LANGUAGE = None
    UI_MENU_SETTINGS_LANGUAGE_EN_US = None
    UI_MENU_SETTINGS_LANGUAGE_ZH_CN = None
    UI_MENU_HELP = None
    UI_MENU_HELP_PROJECT_URL = None
    UI_MENU_HELP_UPDATE = None
    UI_MENU_HELP_UPDATE_TITLE = None
    UI_MENU_HELP_UPDATE_WARNING = None
    UI_MENU_HELP_UPDATE_BUTTON = None
    UI_MENU_HELP_UPDATE_ERROR_SERVER_CONNECTION = None
    UI_MENU_HELP_UPDATE_ERROR_DOWNLOAD_ERROR = None
    UI_MENU_WINDOW = None
    UI_MENU_WINDOW_MESH_VIEWER = None
    UI_MESH_VIEWER_OPTIONS_PANEL = None
    UI_MESH_VIEWER_OPTIONS_PANEL_VERTEX_COLOR = None
    UI_MESH_VIEWER_OPTIONS_PANEL_ADJUST_CAMERA = None
    UI_MESH_VIEWER_OPTIONS_PANEL_AUTO_UPDATE_NODE = None
    UI_MESH_VIEWER_OPTIONS_PANEL_DISPLAY_AXIS_GRID = None
    UI_MESH_VIEWER_INFO_VERTEX = None
    UI_MESH_VIEWER_INFO_POLYGON = None
    UI_TWIRL_EXPANSION_DESCRIPTION = None
    UI_TWIRL_COLLAPSE_DESCRIPTION = None
    UI_COOK_TITLE = None
    UI_COOK_TIME_LABEL = None
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
            LANG_STR_ENUM.ERROR_TITLE: {LANG_ENUM.EN_US: "Error", LANG_ENUM.ZH_CN: "错误"},
            LANG_STR_ENUM.ERROR_INVALID_FILE_PATH: {LANG_ENUM.EN_US: "Invalid File Path", LANG_ENUM.ZH_CN: "无效的文件路径"},
            LANG_STR_ENUM.UI_APP_TITLE: {LANG_ENUM.EN_US: "Portable Houdini", LANG_ENUM.ZH_CN: "Portable Houdini"},
            LANG_STR_ENUM.ERROR_PYLIB_PATH: {LANG_ENUM.EN_US: "Houdini pylib path not exist.", LANG_ENUM.ZH_CN: "Houdini Pylib路径不存在"},
            LANG_STR_ENUM.UI_MENU_FILE: {LANG_ENUM.EN_US: "File", LANG_ENUM.ZH_CN: "文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA: {LANG_ENUM.EN_US: "Open HDA", LANG_ENUM.ZH_CN: "打开HDA"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE: {LANG_ENUM.EN_US: "Open HDA File", LANG_ENUM.ZH_CN: "打开HDA文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP: {LANG_ENUM.EN_US: "Open HIP", LANG_ENUM.ZH_CN: "打开HIP"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE: {LANG_ENUM.EN_US: "Open HIP File", LANG_ENUM.ZH_CN: "打开HIP文件"},
            LANG_STR_ENUM.UI_MENU_FILE_OPEN_RECENT: {LANG_ENUM.EN_US: "Open Recent File", LANG_ENUM.ZH_CN: "打开最近文件"},
            LANG_STR_ENUM.UI_MENU_FILE_SAVE_HIP: {LANG_ENUM.EN_US: "Save debug HIP File", LANG_ENUM.ZH_CN: "保存debug hip文件"},
            LANG_STR_ENUM.UI_MENU_FILE_SAVE_HIP_FILE_DIALOG_TITLE: {LANG_ENUM.EN_US: "Save debug HIP File", LANG_ENUM.ZH_CN: "保存debug hip文件"},
            LANG_STR_ENUM.UI_MENU_SETTINGS: {LANG_ENUM.EN_US: "Settings", LANG_ENUM.ZH_CN: "设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_SAVE: {LANG_ENUM.EN_US: "Save Settings", LANG_ENUM.ZH_CN: "保存设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_GENERAL: {LANG_ENUM.EN_US: "General Settings", LANG_ENUM.ZH_CN: "常规设置"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_HOUDINI_ROOT: {LANG_ENUM.EN_US: "Houdini Root", LANG_ENUM.ZH_CN: "Houdini根目录"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE: {LANG_ENUM.EN_US: "Language (Restart required)", LANG_ENUM.ZH_CN: "语言(重启生效)"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_EN_US: {LANG_ENUM.EN_US: "English", LANG_ENUM.ZH_CN: "English"},
            LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_ZH_CN: {LANG_ENUM.EN_US: "中文", LANG_ENUM.ZH_CN: "中文"},
            LANG_STR_ENUM.UI_MENU_HELP: {LANG_ENUM.EN_US: "Help", LANG_ENUM.ZH_CN: "帮助"},
            LANG_STR_ENUM.UI_MENU_HELP_PROJECT_URL: {LANG_ENUM.EN_US: "Project Link", LANG_ENUM.ZH_CN: "项目链接"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE: {LANG_ENUM.EN_US: "Update", LANG_ENUM.ZH_CN: "更新"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE_TITLE: {LANG_ENUM.EN_US: "Update Application", LANG_ENUM.ZH_CN: "更新应用"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE_WARNING: {LANG_ENUM.EN_US: "Clicking the update button will forcibly clear all files of the current tool\nIf you have modified any source files locally, please back them up promptly\nThe software will exit after the update is complete.", LANG_ENUM.ZH_CN: "点击更新按钮后将会强制清除当前工具的所有文件\n如在本地有修改源文件请及时备份\n更新完成后会退出软件。"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE_BUTTON: {LANG_ENUM.EN_US: "Force Update", LANG_ENUM.ZH_CN: "强制更新"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE_ERROR_SERVER_CONNECTION: {LANG_ENUM.EN_US: "Failed to connect to server!", LANG_ENUM.ZH_CN: "连接服务器失败！"},
            LANG_STR_ENUM.UI_MENU_HELP_UPDATE_ERROR_DOWNLOAD_ERROR: {LANG_ENUM.EN_US: "Encounter some errors when downloading!", LANG_ENUM.ZH_CN: "下载过程中发生错误！"},
            LANG_STR_ENUM.UI_MENU_WINDOW: {LANG_ENUM.EN_US: "Window", LANG_ENUM.ZH_CN: "窗口"},
            LANG_STR_ENUM.UI_MENU_WINDOW_MESH_VIEWER: {LANG_ENUM.EN_US: "Mesh Viewer", LANG_ENUM.ZH_CN: "模型预览窗口"},
            LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL: {LANG_ENUM.EN_US: "Options", LANG_ENUM.ZH_CN: "选项"},
            LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_ADJUST_CAMERA: {LANG_ENUM.EN_US: "Auto Move Camera", LANG_ENUM.ZH_CN: "自动回正摄像机"},
            LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_VERTEX_COLOR: {LANG_ENUM.EN_US: "Display Vertex Color", LANG_ENUM.ZH_CN: "显示顶点色"},
            LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_AUTO_UPDATE_NODE: {LANG_ENUM.EN_US: "Auto Update Model", LANG_ENUM.ZH_CN: "自动更新模型"},
            LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_DISPLAY_AXIS_GRID: {LANG_ENUM.EN_US: "Display Axis Grid", LANG_ENUM.ZH_CN: "显示坐标平面"},
            LANG_STR_ENUM.UI_MESH_VIEWER_INFO_VERTEX: {LANG_ENUM.EN_US: "Vertices", LANG_ENUM.ZH_CN: "顶点数"},
            LANG_STR_ENUM.UI_MESH_VIEWER_INFO_POLYGON: {LANG_ENUM.EN_US: "Triangles", LANG_ENUM.ZH_CN: "三角面数"},
            LANG_STR_ENUM.UI_HDAPANEL_EMPTY_HDA: {LANG_ENUM.EN_US: "Select a HDA", LANG_ENUM.ZH_CN: "打开一个HDA"},
            LANG_STR_ENUM.UI_HDAPANEL_AUTO_RECOOK: {LANG_ENUM.EN_US: "Auto Recook", LANG_ENUM.ZH_CN: "自动计算"},
            LANG_STR_ENUM.UI_HDAPANEL_FORCE_RECOOK: {LANG_ENUM.EN_US: "Force Recook", LANG_ENUM.ZH_CN: "强制重新计算"},
            LANG_STR_ENUM.UI_HDAPANEL_BATCH_LABEL: {LANG_ENUM.EN_US: "Batches: ", LANG_ENUM.ZH_CN: "批处理数: "},
            LANG_STR_ENUM.UI_HDAPANEL_BATCH_BUTTON: {LANG_ENUM.EN_US: "Batching", LANG_ENUM.ZH_CN: "批处理"},
            LANG_STR_ENUM.UI_TWIRL_EXPANSION_DESCRIPTION: {LANG_ENUM.EN_US: "⇓Click to Expand Batching/Recook settings⇓", LANG_ENUM.ZH_CN: "⇓点击展开批处理/重计算设置⇓"},
            LANG_STR_ENUM.UI_TWIRL_COLLAPSE_DESCRIPTION: {LANG_ENUM.EN_US: "⇑Click to Collapse Batching/Recook settings⇑", LANG_ENUM.ZH_CN: "⇑点击收起批处理/重计算设置⇑"},
            LANG_STR_ENUM.UI_COOK_TITLE: {LANG_ENUM.EN_US: "Cooking", LANG_ENUM.ZH_CN: "计算中"},
            LANG_STR_ENUM.UI_COOK_TIME_LABEL: {LANG_ENUM.EN_US: "Time: ", LANG_ENUM.ZH_CN: "时间: "},
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
