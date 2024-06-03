from PySide2.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QSlider, QGroupBox, QStyle, QSizePolicy,
                               QSpinBox, QPushButton, QCheckBox, QLabel, QComboBox, QHBoxLayout, QDoubleSpinBox)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFontMetrics, QColor, QBrush, QPalette
from qwidget.qt_float_slider import QFloatSlider
from qwidget.qt_int_slider import QIntegerSlider
from qwidget.qt_file_string import QFileString
from qwidget.qt_color_selector import QColorSelector
from qwidget.qt_vector_spinbox import QIntVectorSpinBox, QFloatVectorSpinBox
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from hou_parms_model import HouParamTypeEnum, HouParamMetaEnum
from batch_panel import BatchPanel
from functools import partial

class HDAPanel(QWidget):
    _model = None
    _parms_widget = {}
    _parms_value = {}
    _parms_meta = {}
    _batch_buttons = {}
    _batch_parms_value = {}
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

    def clearHDAData(self):
        self._parms_widget = {}
        self._parms_value = {}
        self._parms_meta = {}
        self._batch_buttons = {}
        self._batch_parms_value = {}
        self._hda_name = ""
        self.clearLayout(self.layout)

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
        self.clearHDAData()

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
                    parm_ui.clicked.connect(partial(self.updateButtonParm, parm_name))

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

                    # 批处理按钮
                    row_height = self.style().pixelMetric(QStyle.PM_TitleBarHeight) * 1.25
                    batch_button = QPushButton("✚")
                    batch_button.setBaseSize(row_height, row_height)
                    batch_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    batch_button.clicked.connect(partial(self.onClickBatchSettingButton, parm_name))
                    self._batch_buttons[parm_name] = batch_button
                    parm_layout.addWidget(batch_button)

                    main_parm_layout.addLayout(parm_layout)

                    # 记录变量值和类型
                    self._parms_value[parm_name] = parm_value
                    self._parms_meta[parm_name] = parm_meta

        group_box = QGroupBox(self._hda_name)
        group_box.setLayout(main_parm_layout)
        self.layout.addWidget(group_box)

        bottom_info_layout = QHBoxLayout()
        # batch size
        self.batch_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_BATCH_LABEL) + str(self.getBatchCount()))
        batch_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_BATCH_BUTTON))
        batch_button.clicked.connect(self.onClickBatchButton)

        # auto recook
        self.auto_recook_checkbox = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_AUTO_RECOOK))
        self.auto_recook_checkbox.setChecked(True)
        self.force_recook_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_FORCE_RECOOK))
        self.force_recook_button.clicked.connect(self.updateAllParms)

        # 创建两个 GroupBox
        batch_groupbox = QGroupBox()
        batch_groupbox.setMaximumHeight(60)
        batch_layout = QHBoxLayout(batch_groupbox)
        batch_layout.addWidget(self.batch_label)
        batch_layout.addWidget(batch_button)

        recook_groupbox = QGroupBox()
        recook_groupbox.setMaximumHeight(60)
        recook_layout = QHBoxLayout(recook_groupbox)
        recook_layout.addWidget(self.auto_recook_checkbox)
        recook_layout.addWidget(self.force_recook_button)

        # 创建一个水平布局来排列两个 GroupBox
        groupbox_layout = QHBoxLayout()
        groupbox_layout.addWidget(batch_groupbox)
        groupbox_layout.addWidget(recook_groupbox)

        # 将水平布局添加到底部信息布局
        bottom_info_layout.addLayout(groupbox_layout)

        self.layout.addLayout(bottom_info_layout)

    def getBatchCount(self):
        batch_count = 0
        if self._batch_parms_value:
            for _, batch_parm in self._batch_parms_value.items():
                batch_count = max(len(batch_parm), batch_count)

        return batch_count

    def updateBatchIcons(self, parm_name):
        self.batch_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_HDAPANEL_BATCH_LABEL) + str(self.getBatchCount()))
        if parm_name in self._batch_parms_value.keys() and parm_name in self._batch_buttons.keys():
            parm_batch_count = len(self._batch_parms_value[parm_name])
            button = self._batch_buttons[parm_name]
            if parm_batch_count > 0:
                button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
                button.setText("✚:" + str(parm_batch_count))
                button.adjustSize()
                button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                button.setStyleSheet("background-color: darkslateblue; color: white;")
                self.updateParmBatchToolTips(parm_name)
            else:
                button.setText("✚")
                button.setStyleSheet("")

    def updateParmBatchToolTips(self, parm_name):
        if parm_name in self._batch_parms_value.keys() and parm_name in self._batch_buttons.keys():
            parm_batch_count = len(self._batch_parms_value[parm_name])
            button = self._batch_buttons[parm_name]
            tooltip = ""
            parm_batch_count = len(self._batch_parms_value[parm_name])
            parm_meta = self._parms_meta[parm_name]
            parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
            if parm_batch_count > 0:
                tooltip = "<table border='1' style='border-collapse: collapse;'>"
                tooltip += "<tr><th>Index</th><th>Value</th></tr>"
                idx = 1
                for value in self._batch_parms_value[parm_name]:
                    if parm_type == HouParamTypeEnum.COMBOX:
                        parm_combox = parm_meta.getData(HouParamMetaEnum.COMBOX_DEFINE)
                        combox_labels = parm_combox.labels
                        value = combox_labels[value]

                    tooltip += "<tr><td>{}</td><td>{}</td></tr>".format(idx, str(value))
                    idx += 1
                tooltip += "</table>"

            button.setToolTip(tooltip)

    def onClickBatchButton(self):
        batch_count = self.getBatchCount()
        for i in range(batch_count):
            batch_value_dict = {}
            buttons_name = []
            for _, parm_meta in self._parms_meta.items():
                parm_value = parm_meta.getData(HouParamMetaEnum.VALUE)
                parm_name = parm_meta.getData(HouParamMetaEnum.NAME)
                parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
                if parm_type == HouParamTypeEnum.BUTTON:
                    buttons_name.append(parm_name)

                if parm_name in self._batch_parms_value.keys():
                    parm_batches_value = self._batch_parms_value[parm_name]
                    # 若数组越界则使用默认值
                    parm_value = parm_batches_value[i] if i < len(parm_batches_value) else parm_value
                    if parm_value is None:
                        parm_value = parm_meta.getData(HouParamMetaEnum.VALUE)
                    # @TODO button需要判断是否需要点击
                batch_value_dict[parm_name] = parm_value

            self.updateBatchParms(batch_value_dict)
            # 先设置参数 后点击按钮
            for button_name in buttons_name:
                self.updateButtonParm(button_name, update_parms=False)

    # 设置属性批处理值按钮
    def onClickBatchSettingButton(self, parm_name):
        parm_meta = self._parms_meta[parm_name]
        parm_meta.setDataSpecific(HouParamMetaEnum.VALUE, self._parms_value[parm_name])
        self.batch_panel = BatchPanel(parm_meta, self._batch_parms_value[parm_name] if parm_name in self._batch_parms_value.keys() else None)
        self.batch_panel.on_save_batch_info.connect(self.updateBatchInfo)
        self.batch_panel.show()

    def updateBatchInfo(self, parm_name, parms_value):
        self._batch_parms_value[parm_name] = parms_value
        self.updateBatchIcons(parm_name)

    def updateParm(self, parm_name, parm_value):
        if self._model is not None:
            self._parms_value[parm_name] = parm_value
            if self.auto_recook_checkbox.isChecked():
                self._model.setParmFromView(parm_name, parm_value)

    # 不论是否开启auto recook，按下按钮都会触发事件
    def updateButtonParm(self, parm_name, update_parms=True):
        if self._model is not None:
            if update_parms:
                self.updateAllParms()
            self._model.setParmFromView(parm_name, None)

    def updateStrParm(self, parm_name):
        parm_value = self._parms_widget[parm_name].text()
        if self._model is not None:
            self._parms_value[parm_name] = parm_value
            if self.auto_recook_checkbox.isChecked():
                self._model.setParmFromView(parm_name, parm_value)
    def updateAllParms(self):
        if self._model is not None:
            self._model.setParmsFromView(self._parms_value)

    def updateBatchParms(self, key_value_dict):
        if self._model is not None:
            self._model.setParmsFromView(key_value_dict)
