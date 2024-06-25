from panel.utils.globals import SETTINGS_MANAGER, SettingsEnum
import qdarktheme


class Theme:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Theme, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            qdarktheme.enable_hi_dpi()
            self.additional_qss = """
            QToolTip {
                color: silver; /* 字体颜色 */
                background-color: #08101F; /* 背景颜色 */
                border: 1px solid white;
            }
            """
            self._initialized = True

    # call this after setting up app
    def setTheme(self):
        qdarktheme.setup_theme(SETTINGS_MANAGER.get(SettingsEnum.THEME), additional_qss=self.additional_qss)
