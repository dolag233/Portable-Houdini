from hou_parms_model import HouParamMetaEnum, HouParamTypeEnum
from utils.globals import APP
from qwidget.qt_progress_bar import QProgressBarWidget
from PySide2.QtCore import QTimer, Qt, Signal, QObject, QThread
from queue import Queue
import threading
import time
import os
import copy

class HDAController(QObject):
    cook_started = Signal()
    cook_finished = Signal()
    update_display_model = Signal(list, list, list)  # [vertices, vertex_colors, faces]
    _CUR_HDA_PATH = None
    _CUR_HDA_NAME = None
    _CUR_HIP_PATH = None
    _CUR_HIP_NAME = None
    _cur_hda_def = None
    _cur_hda_node = None
    _node_parms = None
    _model = None
    _last_model_update_time = 0
    _model_update_interval = 0.005

    def __init__(self, model):
        super().__init__()
        self._model = model
        self._model.view_data_changed.connect(self.queueWriteHDAProperty)
        self._model.view_datas_changed.connect(self.queueWriteHDAProperties, Qt.BlockingQueuedConnection)

        self.queue = Queue()
        self.worker_thread = threading.Thread(target=self.processQueue)
        self.worker_thread.daemon = True  # Ensure the thread exits when the main program exits
        self.worker_thread.start()

        self._last_model_update_time = time.time()

    def queueWriteHDAProperty(self, parm_meta):
        parm_meta_data = {
            'type': parm_meta.getData(HouParamMetaEnum.TYPE),
            'name': parm_meta.getData(HouParamMetaEnum.NAME),
            'parm_tuple_ref': parm_meta.getData(HouParamMetaEnum.PARM_TUPLE_REF),
            'value': parm_meta.getData(HouParamMetaEnum.VALUE)
        }
        self.queue.put(("parm", parm_meta_data))

    def queueWriteHDAProperties(self, parm_metas):
        parm_metas_data = []
        for parm_meta in parm_metas:
            parm_meta_data = {
                'type': parm_meta.getData(HouParamMetaEnum.TYPE),
                'name': parm_meta.getData(HouParamMetaEnum.NAME),
                'parm_tuple_ref': parm_meta.getData(HouParamMetaEnum.PARM_TUPLE_REF),
                'value': parm_meta.getData(HouParamMetaEnum.VALUE)
            }
            parm_metas_data.append(parm_meta_data)
        self.queue.put(("parms", parm_metas_data))

    def processQueue(self):
        while True:
            if self.queue.empty():
                time.sleep(0.5)
                continue
            else:
                process_type, parm_data = self.queue.get()
                if process_type == "parm":
                    self.writeHDAProperty(parm_data)
                elif process_type == "parms":
                    self.writeHDAProperties(parm_data)
                self.queue.task_done()

    def getCurrentHDAPath(self):
        return self._CUR_HDA_PATH

    def getCurrentHIPPath(self):
        return self._CUR_HIP_PATH

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
        if self._CUR_HDA_PATH is None and not os.path.exists(self._CUR_HDA_NAME):
            return False

        try:
            import utils.init_houdini
            import hou
        except ImportError:
            return

        self._cur_hda_def = hou.hda.definitionsInFile(self._CUR_HDA_PATH)[0]
        hou.hipFile.clear(suppress_save_prompt=True)
        hou.hda.installFile(self._CUR_HDA_PATH)
        obj_net = hou.node("/obj")
        geo_net = obj_net.createNode("geo", "geo")
        hda_node = geo_net.createNode(self._cur_hda_def.nodeTypeName(), "hda")
        self._cur_hda_node = hda_node
        if self._cur_hda_node is not None and self._model is not None:
            self._model.setHDANode(self._cur_hda_node)

        self.updateNodeModel()
        return True

    def getCurNode(self):
        return self._cur_hda_node

    def updateHDAProperty(self, parm_value, parm_name):
        if self._model is not None:
            self._model.setParmFromController(parm_value, parm_name)

    def writeHDAProperty(self, parm_meta_data):
        self.cook_started.emit()
        start_time = time.time()
        parm_type = parm_meta_data['type']
        parm_name = parm_meta_data['name']
        parm_tuple_ref = parm_meta_data['parm_tuple_ref']
        parm_value = parm_meta_data['value']
        if not parm_tuple_ref:
            self.cook_finished.emit()
            return

        # button不需要赋值，但需要点击
        if parm_type == HouParamTypeEnum.BUTTON:
            parm_tuple_ref[0].pressButton()
            print("click button {}".format(parm_name))

        elif parm_type in (HouParamTypeEnum.FLOAT_ARRAY, HouParamTypeEnum.INT_ARRAY, HouParamTypeEnum.COLOR):
            re_val = parm_value
            assert len(re_val) == len(parm_value)
            parm_tuple_ref.set(parm_value)
            print('change parm "{}" value to {}'.format(parm_name, parm_value))

        elif parm_type == HouParamTypeEnum.RAMP:
            import hou
            new_ramp = hou.Ramp(parm_value["basis"], parm_value["keys"], parm_value["values"])
            parm_tuple_ref[0].set(new_ramp)
            print('change ramp "{}" value to {}'.format(parm_name, new_ramp))

        else:
            parm_tuple_ref.set((parm_value,))
            print('change parm "{}" value to {}'.format(parm_name, parm_value))

        print("use time: {}".format(time.time() - start_time))
        self.cook_finished.emit()

        if time.time() - self._last_model_update_time > self._model_update_interval:
            self._last_model_update_time = time.time()
            self.updateNodeModel()

    def writeHDAProperties(self, parm_metas_data):
        import hou
        hou.setUpdateMode(hou.updateMode.Manual)

        for parm_meta_data in parm_metas_data:
            if parm_meta_data['type'] != HouParamTypeEnum.BUTTON:
                self.writeHDAProperty(parm_meta_data)

        self._cur_hda_node.cook()

        for parm_meta_data in parm_metas_data:
            if parm_meta_data['type'] == HouParamTypeEnum.BUTTON:
                self.writeHDAProperty(parm_meta_data)

        hou.setUpdateMode(hou.updateMode.AutoUpdate)

    def updateNodeModel(self):
        vertices = []
        faces = []
        vertex_colors = []

        # 读取 Houdini 节点的几何数据
        geometry = self.getCurNode().geometry()
        points = geometry.points()
        polys = geometry.prims()

        # 提取顶点
        use_default_vertex_color = False
        if len(points) > 0:
            if points[0].attribValue("Cd") is None:
                use_default_vertex_color = True
                vertex_colors = [(0.5, 0.5, 0.5)] * len(points)

        for point in points:
            position = point.position()
            vertices.append((position[0], position[1], position[2]))

            # 提取颜色
            if not use_default_vertex_color:
                color = point.attribValue("Cd")
                vertex_colors.append((color[0], color[1], color[2]))

        # 提取面
        for poly in polys:
            poly_vertices = poly.vertices()
            face = []
            for vertex in poly_vertices:
                face.append(vertex.point().number())
            faces.append(face)

        self.update_display_model.emit(vertices, vertex_colors, faces)

    def unloadHDA(self):
        self._CUR_HDA_PATH = None
        self._CUR_HDA_NAME = None
        self._CUR_HIP_PATH = None
        self._CUR_HIP_NAME = None
        self._cur_hda_def = None
        self._cur_hda_node = None
