try:
    import utils.init_houdini
except ImportError:
    pass
from utils.simple_enum import SimpleEnum
from PySide2.QtCore import QObject, Signal


class HouParamTypeEnum(SimpleEnum):
    STRING = None
    FILE_STRING = None
    FLOAT = None
    FLOAT_ARRAY = None
    INT = None
    INT_ARRAY = None
    TOGGLE = None
    BUTTON = None
    RAMP = None
    COMBOX = None
    COLOR = None  # 注意，color有RGB和RGBA两种


class HouParamMetaEnum(SimpleEnum):
    START = None
    NAME = None
    LABEL = None
    TYPE = None
    VALUE = None
    VALUE_RANGE = None
    COMBOX_DEFINE = None  # {'name': , 'label': }
    DESCRIPTION = None
    HELP = None
    PARM_TUPLE_REF = None
    END = None

class HouParmCombox():
    items = []
    labels = []

class HouParmMetadata():
    meta = {}

    def setData(self, parm_name, parm_label, parm_type_enum, parm_value=None, parm_help='', parm_ref=None):
        meta = {}
        meta[HouParamMetaEnum.NAME] = parm_name
        meta[HouParamMetaEnum.LABEL] = parm_label
        meta[HouParamMetaEnum.TYPE] = parm_type_enum
        meta[HouParamMetaEnum.VALUE] = parm_value
        meta[HouParamMetaEnum.PARM_TUPLE_REF] = parm_ref
        meta[HouParamMetaEnum.HELP] = parm_help
        self.meta = meta

    def setDataSpecific(self, parm_meta_enum, value):
        if HouParamMetaEnum.START < parm_meta_enum < HouParamMetaEnum.END:
            self.meta[parm_meta_enum] = value

    def getData(self, parm_meta_enum):
        if self.meta.__contains__(parm_meta_enum):
            return self.meta[parm_meta_enum]
        return None


class HouParmsModel(QObject):
    view_datas_changed = Signal(list)
    view_data_changed = Signal(HouParmMetadata)
    controller_data_changed = Signal(HouParmMetadata)

    parms = []

    def __init__(self):
        super().__init__()

    def clearHDA(self):
        self.parms = []

    def setHDANode(self, node):
        try:
            import utils.init_houdini
            import hou
        except ImportError:
            return
        for parm_tuple in node.parmTuples():
            parm_temp = parm_tuple.parmTemplate()
            parm_label = parm_temp.label()
            parm_type = None
            parm_value = None
            parm_help = parm_tuple.parmTemplate().help()
            parm_range = None
            parm_combox = None
            parm_ramp = None
            # this parm is a sub item of some host item like vector, ramp
            if parm_tuple.isMultiParmInstance():
                continue

            if isinstance(parm_temp, hou.StringParmTemplate):
                if parm_temp.stringType() == hou.stringParmType.FileReference:
                    parm_type = HouParamTypeEnum.FILE_STRING
                else:
                    parm_type = HouParamTypeEnum.STRING
                parm_value = parm_tuple[0].rawValue()

            # scalar
            elif isinstance(parm_temp, hou.FloatParmTemplate) and parm_temp.numComponents() == 1:
                parm_type = HouParamTypeEnum.FLOAT
                parm_value = parm_tuple.eval()[0]
                parm_range = [parm_temp.minValue(), parm_temp.maxValue()]

            # vector
            elif isinstance(parm_temp, hou.FloatParmTemplate) and parm_temp.numComponents() > 1:
                # vector的range不起作用
                if hasattr(parm_tuple, 'evalAsFloats'):
                    parm_type = HouParamTypeEnum.FLOAT_ARRAY
                    parm_value = parm_tuple.evalAsFloats()
                    # 也有可能是颜色属性
                    if parm_temp.namingScheme() == hou.parmNamingScheme.RGBA:
                        parm_type = HouParamTypeEnum.COLOR

                elif hasattr(parm_tuple, 'evalAsFloat'):
                    parm_type = HouParamTypeEnum.FLOAT
                    parm_value = parm_tuple.evalAsFloat()
                else:
                    continue

            elif isinstance(parm_temp, hou.IntParmTemplate) and parm_temp.numComponents() == 1:
                parm_type = HouParamTypeEnum.INT
                parm_value = parm_tuple.eval()[0]
                parm_range = [parm_temp.minValue(), parm_temp.maxValue()]

            elif isinstance(parm_temp, hou.IntParmTemplate) and parm_temp.numComponents() > 1:
                # vector的range不起作用
                if hasattr(parm_tuple, 'evalAsInts'):
                    parm_type = HouParamTypeEnum.INT_ARRAY
                    parm_value = parm_tuple.evalAsInts()
                elif hasattr(parm_tuple, 'evalAsInt'):
                    parm_type = HouParamTypeEnum.INT
                    parm_value = parm_tuple.evalAsInt()
                else:
                    continue

            elif isinstance(parm_temp, hou.ToggleParmTemplate):
                parm_type = HouParamTypeEnum.TOGGLE
                parm_value = parm_tuple.eval()[0]

            elif isinstance(parm_temp, hou.ButtonParmTemplate):
                parm_type = HouParamTypeEnum.BUTTON

            # combox
            elif isinstance(parm_temp, hou.MenuParmTemplate):
                parm_type = HouParamTypeEnum.COMBOX
                parm_combox = HouParmCombox()
                parm_combox.items = parm_temp.menuItems()
                parm_combox.labels = parm_temp.menuLabels()
                parm_value = parm_tuple.eval()[0]

            # ramp
            elif isinstance(parm_temp, hou.RampParmTemplate):
                parm_type = HouParamTypeEnum.RAMP
                parm_value = parm_tuple.eval()[0]
                parm_value = {'keys': parm_value.keys(), 'values': parm_value.values(), 'basis': parm_value.basis()}

            parm_meta = HouParmMetadata()
            if parm_type is not None:
                parm_meta.setData(parm_tuple.name(), parm_label, parm_type, parm_value, parm_help, parm_tuple)
                if parm_range is not None:
                    parm_meta.setDataSpecific(HouParamMetaEnum.VALUE_RANGE, parm_range)

                if parm_combox is not None:
                    parm_meta.setDataSpecific(HouParamMetaEnum.COMBOX_DEFINE, parm_combox)

                if parm_ramp is not None:
                    parm_meta.setDataSpecific(HouParamMetaEnum.RAMP_DEFINE, parm_ramp)

                self.parms.append(parm_meta)

    def getParms(self):
        return self.parms

    def setParmFromView(self, index_or_key, parm_value):
        self.__setParm(index_or_key, parm_value)
        parm_meta = self.getParmMeta(index_or_key)
        if parm_meta:
            self.view_data_changed.emit(parm_meta)

    def setParmsFromView(self, key_value_dict):
        parm_metas = []
        for index_or_key, parm_value in key_value_dict.items():
            parm_meta = self.getParmMeta(index_or_key)
            parm_meta.setDataSpecific(HouParamMetaEnum.VALUE, parm_value)
            parm_metas.append(parm_meta)
        self.view_datas_changed.emit(parm_metas)

    def setParmFromController(self, index_or_key, parm_value):
        self.__setParm(index_or_key, parm_value)
        parm_meta = self.getParmMeta(index_or_key)
        if parm_meta:
            self.controller_data_changed.emit(parm_meta)

    def getParmMeta(self, index_or_key):
        if isinstance(index_or_key, int):
            if 0 <= index_or_key < len(self.parms):
                return self.parms[index_or_key]

        elif isinstance(index_or_key, str):
            for parm in self.parms:
                if parm.getData(HouParamMetaEnum.NAME) == index_or_key:
                    return parm

        return None

    # 为遵循MVC框架，真正的Houdini数据修改部分放到Controller中进行
    def __setParm(self, index_or_key, new_parm_value):
        parm_meta = self.getParmMeta(index_or_key)
        parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
        # button不需要赋值
        if parm_type == HouParamTypeEnum.BUTTON:
            return

        elif parm_type == HouParamTypeEnum.FLOAT_ARRAY:
            re_val = parm_meta.getData(HouParamMetaEnum.VALUE)
            assert len(re_val) == len(new_parm_value)
            parm_meta.setDataSpecific(HouParamMetaEnum.VALUE, new_parm_value)

        else:
            parm_meta.setDataSpecific(HouParamMetaEnum.VALUE, new_parm_value)

    _index = 0

    def __getitem__(self, index_or_key):
        if isinstance(index_or_key, int):
            if 0 <= index_or_key < len(self.parms):
                return self.parms[index_or_key]

            raise IndexError

        elif isinstance(index_or_key, str):
            for parm in self.parms:
                if parm.getData(HouParamMetaEnum.NAME) == index_or_key:
                    return parm

            raise KeyError

        raise IndexError

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.parms):
            self._index += 1
            return self.parms[self._index]

        else:
            raise StopIteration

