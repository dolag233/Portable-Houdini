from hou_parms_model import HouParamMetaEnum, HouParamTypeEnum
import os
import sys

class HDAController:
    _CUR_HDA_PATH = None
    _CUR_HDA_NAME = None
    _CUR_HIP_PATH = None
    _CUR_HIP_NAME = None
    _cur_hda_def = None
    _cur_hda_node = None
    _node_parms = None
    _model = None

    def __init__(self, model):
        self._model = model
        self._model.view_data_changed.connect(self.writeHDAProperty)
        self._model.view_datas_changed.connect(self.writeHDAProperties)

    def getCurrentHDAPath(self):
        if self._CUR_HDA_PATH is not None:
            return self._CUR_HDA_PATH

        return None

    def getCurrentHIPPath(self):
        if self._CUR_HIP_PATH is not None:
            return self._CUR_HIP_PATH

        return None

    def checkValid(self):
        return (self._CUR_HDA_PATH is not None) or (self._CUR_HIP_PATH is not None)

    def setCurHDAPath(self, hda_path):
        self._CUR_HDA_PATH = hda_path

    def setCurHDAName(self, hda_name):
        self._CUR_HDA_NAME = hda_name

    def setCurHIPPath(self, hip_path):
        self._CUR_HIP_PATH = hip_path

    def setCurHIPName(self, hip_name):
        self._CUR_HIP_NAME = hip_name

    def clearHDA(self):
        try:
            import utils.init_houdini
            import hou
        except ImportError:
            return

        hou.hipFile.clear(suppress_save_prompt=True)

    def loadHDA(self):
        if self._CUR_HDA_PATH is None and os.path.exists(self._CUR_HDA_NAME):
            return False

        try:
            import utils.init_houdini
            import hou
        except ImportError:
            return

        _cur_hda_def = hou.hda.definitionsInFile(self._CUR_HDA_PATH)[0]
        # 创建临时hip并创建hda节点
        hou.hipFile.clear(suppress_save_prompt=True)
        hou.hda.installFile(self._CUR_HDA_PATH)
        obj_net = hou.node("/obj")
        geo_net = obj_net.createNode("geo", "geo")
        hda_node = geo_net.createNode(_cur_hda_def.nodeTypeName(), "hda")  # 目前hda的路径是/obj/geo/hda
        self._cur_hda_node = hda_node
        if self._cur_hda_node is not None and self._model is not None:
            self._model.setHDANode(self._cur_hda_node)

        return True

    def updateHDAProperty(self, parm_value, parm_name):
        if self._model is not None:
            self._model.setParmFromController(parm_value, parm_name)

    # @TODO 这个函数需要链接到个signal
    def writeHDAProperty(self, parm_meta):
        parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
        parm_name = parm_meta.getData(HouParamMetaEnum.NAME)
        parm_tuple_ref = parm_meta.getData(HouParamMetaEnum.PARM_TUPLE_REF)
        parm_value = parm_meta.getData(HouParamMetaEnum.VALUE)
        if not parm_tuple_ref:
            return

        # button不需要赋值，但需要点击
        if parm_type == HouParamTypeEnum.BUTTON:
            parm_tuple_ref[0].pressButton()
            return

        elif parm_type == HouParamTypeEnum.FLOAT_ARRAY or parm_type == HouParamTypeEnum.INT_ARRAY or\
            parm_type == HouParamTypeEnum.COLOR:
            re_val = parm_meta.getData(HouParamMetaEnum.VALUE)
            assert len(re_val) == len(parm_value)
            parm_tuple_ref.set(parm_value)

        else:
            # 因为是parm tuple, 所以要设置tuple值
            parm_tuple_ref.set((parm_value,))

        print('change parm "{}" value to {}'.format(parm_name, parm_value))

    def writeHDAProperties(self, parm_metas):
        if self._cur_hda_node:
            self._cur_hda_node.setAutoCooking(False)

            for parm_meta in parm_metas:
                # force recook的时候并不会点击所有的按钮。但是如果是这样，那么force recook有什么用呢
                if parm_meta.getData(HouParamMetaEnum.TYPE) != HouParamTypeEnum.BUTTON:
                    self.writeHDAProperty(parm_meta)

            self._cur_hda_node.cook()
            self._cur_hda_node.setAutoCooking(True)

    def unloadHDA(self):
        self._CUR_HDA_PATH = None
        self._CUR_HDA_NAME = None
        self._CUR_HIP_PATH = None
        self._CUR_HIP_NAME = None
        self._cur_hda_def = None
        self._cur_hda_node = None

