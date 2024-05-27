from language_enum import LANG_ENUM

HFS = r"D:\Houdini 19.5"
LANGUAGE = LANG_ENUM.ZH_CN


def setLanguage(language_idx):
    global LANGUAGE
    if language_idx == 0:
        LANGUAGE = LANG_ENUM.ZH_CN
    elif language_idx == 1:
        LANGUAGE = LANG_ENUM.EN_US
