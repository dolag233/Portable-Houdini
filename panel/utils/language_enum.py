from panel.utils.simple_enum import SimpleEnum


class LANG_ENUM(SimpleEnum):
    EN_US = None
    ZH_CN = None


def LangStrToEnum(language_str):
    res = LANG_ENUM.EN_US
    if language_str == "zh_cn":
        res = LANG_ENUM.ZH_CN
    elif language_str == "en_us":
        res = LANG_ENUM.EN_US
    return res


def LangEnumToStr(language_enum):
    res = "en_us"
    if language_enum == LANG_ENUM.EN_US:
        res = "en_us"
    elif language_enum == LANG_ENUM.ZH_CN:
        res = "zh_cn"
    return res
