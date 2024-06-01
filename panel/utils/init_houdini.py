import os
import sys
from localization import LANG_STR_ENUM, getLocalizationStr
from settings_manager import SettingsEnum
from globals import SETTINGS_MANAGER
from PySide2.QtWidgets import QApplication, QMessageBox

if 'hou' not in sys.modules:
    print("Try to initialize Houdini environment")

    valid_houdini_path = True
    HOUDINI_PATH = SETTINGS_MANAGER.get(SettingsEnum.HOUDINI_PATH)

    # get pylib path
    if not os.path.isdir(HOUDINI_PATH) or not os.path.isdir(os.path.join(HOUDINI_PATH, "houdini")):
        valid_houdini_path = False

    PYLIB_PATH = None
    if valid_houdini_path:
        for file in os.listdir(os.path.join(HOUDINI_PATH, "houdini")):
            if "python" in file and "libs" in file:
                if "hou.py" in os.listdir(os.path.join(HOUDINI_PATH, "houdini", file)):
                    PYLIB_PATH = os.path.join(HOUDINI_PATH, "houdini", file)
                    break

        if not PYLIB_PATH:
            valid_houdini_path = False

    if valid_houdini_path:
        os.environ["HHP"] = PYLIB_PATH
        os.environ["HFS"] = HOUDINI_PATH
        os.environ["PATH"] = "{}/bin;".format(os.environ["HFS"]) + PYLIB_PATH

    if not valid_houdini_path:
        msg_box = QMessageBox(QMessageBox.Warning, getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH),
                              getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH_SETTINGS))
        msg_box.exec_()
        raise ImportError("Invalid Houdini Path")

    if valid_houdini_path:
        # prepare houdini env
        if hasattr(sys, "setdlopenflags"):
            old_dlopen_flags = sys.getdlopenflags()
            sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)

        if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
            os.add_dll_directory("{}/bin".format(os.environ["HFS"]))

        # restore PATH after initializing houdini
        os_path = os.environ.get("path")
        try:
            import hou
        except ImportError:
            sys.path.append(os.environ['HHP'])
            import hou
        finally:
            if hasattr(sys, "setdlopenflags"):
                sys.setdlopenflags(old_dlopen_flags)

        os.environ["path"] += ";" + os_path

        print("Houdini environment initialized!")
