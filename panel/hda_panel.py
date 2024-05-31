from PySide2.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QSlider, QGroupBox,
                               QSpinBox, QPushButton, QCheckBox, QLabel, QComboBox, QHBoxLayout, QDoubleSpinBox)
from PySide2.QtCore import Qt
from qwidget.qt_float_slider import QFloatSlider
from qwidget.qt_int_slider import QIntegerSlider
from qwidget.qt_file_string import QFileString
from qwidget.qt_color_selector import QColorSelector
from qwidget.qt_vector_spinbox import QIntVectorSpinBox, QFloatVectorSpinBox
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from hou_parms_model import HouParamTypeEnum, HouParamMetaEnum
from functools import partial

class HDAPanel(QWidget):
    _model = None
    _parms_widget = {}
    _parms_value = {}
    _hda_name = ""

    def __init__(self, model):
        super().__init__()
        self.initUI()
        self._model = model

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # HDA name
        hda_name = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_EMPTY_HDA))
        self.layout.addWidget(hda_name)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def setHDAName(self, name):
        self._hda_name = name

    def updateUI(self):
        self.clearLayout(self.layout)

        main_parm_layout = QVBoxLayout()
        if self._model is not None:
            parms_meta = self._model.getParms()
            for parm_meta in parms_meta:
                parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
                parm_value = parm_meta.getData(HouParamMetaEnum.VALUE)
                parm_name = parm_meta.getData(HouParamMetaEnum.NAME)
                parm_label = parm_meta.getData(HouParamMetaEnum.LABEL)
                parm_range = parm_meta.getData(HouParamMetaEnum.VALUE_RANGE)
                parm_combox = parm_meta.getData(HouParamMetaEnum.COMBOX_DEFINE)
                parm_ui = None
                parm_layout = QHBoxLayout()
                parm_label_ui = QLabel(parm_label)

                if parm_type == HouParamTypeEnum.STRING:
                    parm_ui = QLineEdit()
                    parm_ui.setText(parm_value)
                    parm_ui.returnPressed.connect(partial(self.updateStrParm, parm_name))

                elif parm_type == HouParamTypeEnum.FILE_STRING:
                    parm_ui = QFileString()
                    parm_ui.setText(parm_value)
                    parm_ui.filePathEntered.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.FLOAT:
                    parm_ui = QFloatSlider(Qt.Horizontal)
                    parm_ui.setRange(parm_range[0], parm_range[1])
                    print(parm_value)
                    parm_ui.setValue(parm_value)
                    parm_ui.floatValueChanged.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.FLOAT_ARRAY:
                    array_len = len(parm_value)
                    parm_ui = QFloatVectorSpinBox(vector_length=array_len)
                    if parm_range is not None:
                        parm_ui.setRange(parm_range[0], parm_range[1])

                    parm_ui.setValue(parm_value)
                    parm_ui.valueChanged.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.COLOR:
                    array_len = len(parm_value)
                    use_alpha = False if array_len == 3 else True
                    parm_ui = QColorSelector(use_alpha=use_alpha, use_color01=True)
                    parm_ui.setValue(parm_value)
                    parm_ui.valueChanged01.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.INT:
                    parm_ui = QIntegerSlider(Qt.Horizontal)
                    parm_ui.setRange(parm_range[0], parm_range[1])
                    parm_ui.setValue(parm_value)
                    parm_ui.valueChanged.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.INT_ARRAY:
                    array_len = len(parm_value)
                    parm_ui = QIntVectorSpinBox(vector_length=array_len)
                    if parm_range is not None:
                        parm_ui.setRange(parm_range[0], parm_range[1])

                    parm_ui.setValue(parm_value)
                    parm_ui.valueChanged.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.TOGGLE:
                    parm_ui = QCheckBox()
                    parm_ui.setChecked(parm_value)
                    parm_ui.stateChanged.connect(partial(self.updateParm, parm_name))

                elif parm_type == HouParamTypeEnum.BUTTON:
                    parm_ui = QPushButton(parm_label)
                    parm_ui.clicked.connect(partial(self.updateParm, parm_name, 0))

                elif parm_type == HouParamTypeEnum.COMBOX:
                    parm_ui = QComboBox()
                    items = parm_combox.items
                    labels = parm_combox.labels
                    parm_ui.addItems(labels)
                    parm_ui.setCurrentIndex(parm_value)
                    parm_ui.currentIndexChanged.connect(partial(self.updateParm, parm_name))

                if parm_ui is not None:
                    self._parms_widget[parm_name] = parm_ui
                    # button不需要label
                    if parm_type != HouParamTypeEnum.BUTTON:
                        parm_layout.addWidget(parm_label_ui)
                    parm_layout.addWidget(parm_ui)

                    main_parm_layout.addLayout(parm_layout)

                    # 记录变量值
                    self._parms_value[parm_name] = parm_value

        group_box = QGroupBox(self._hda_name)
        group_box.setLayout(main_parm_layout)
        self.layout.addWidget(group_box)

        # auto recook
        recook_layout = QHBoxLayout()
        self.auto_recook_checkbox = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_AUTO_RECOOK))
        self.auto_recook_checkbox.setChecked(True)
        recook_layout.addWidget(self.auto_recook_checkbox)

        self.force_recook_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_FORCE_RECOOK))
        self.force_recook_button.clicked.connect(self.updateAllParms)
        recook_layout.addWidget(self.force_recook_button)

        self.layout.addLayout(recook_layout)

    def updateParm(self, parm_name, parm_value):
        if self._model is not None:
            self._parms_value[parm_name] = parm_value
            if self.auto_recook_checkbox.isChecked():
                self._model.setParmFromView(parm_name, parm_value)

    def updateStrParm(self, parm_name):
        parm_value = self._parms_widget[parm_name].text()
        if self._model is not None:
            self._parms_value[parm_name] = parm_value
            if self.auto_recook_checkbox.isChecked():
                self._model.setParmFromView(parm_name, parm_value)
    def updateAllParms(self):
        if self._model is not None:
            for parm_name, parm_value in self._parms_value.items():
                self._model.setParmFromView(parm_name, parm_value)
