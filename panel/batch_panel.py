import sys
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QDialog,
    QTableWidgetItem, QPushButton, QScrollArea, QHeaderView, QMessageBox, QFileDialog,
    QLineEdit, QSlider, QGroupBox, QStyle, QPushButton, QCheckBox, QLabel, QComboBox, QDoubleSpinBox
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFontMetrics, QColor, QBrush, QPalette
from hou_parms_model import HouParamTypeEnum, HouParamMetaEnum
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from qwidget.qt_vector_spinbox import QIntVectorSpinBox, QFloatVectorSpinBox
from qwidget.qt_float_slider import QFloatSlider
from qwidget.qt_file_string import QFileString
from qwidget.qt_int_slider import QIntegerSlider
from qwidget.qt_color_selector import QColorSelector
from qwidget.qt_ramp import QRampWidget, QRamp
from functools import partial

class BatchPanel(QDialog):
    on_save_batch_info = Signal(str, list)  # (name, value_list)

    def __init__(self, parm_meta, default_batches_value):
        super().__init__()
        self._parm_meta = parm_meta
        self._default_batches_value = default_batches_value
        self.initUI()

    def initUI(self):
        parm_label = self._parm_meta.getData(HouParamMetaEnum.LABEL)
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_TITLE) + " - " + parm_label)
        self.setGeometry(100, 100, 400, 500)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建表格
        self.table_widget = QTableWidget(0, 2)
        self.table_widget.setHorizontalHeaderLabels([getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_INDEX),
                                                     getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_VALUE)])
        # 设置第一列的宽度
        default_font = self.font()
        font_metrics = QFontMetrics(default_font)
        text_width = font_metrics.width(getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_INDEX))
        self.table_widget.setColumnWidth(0, text_width + 20)
        # 第二列宽度随窗口变化
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 让第二列自动
        self.table_widget.verticalHeader().setVisible(False)

        # 创建按钮
        btn_add = QPushButton("✚")
        btn_remove = QPushButton("━")
        btn_clear = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_CLEAR))
        btn_import = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_IMPORT))

        # 连接按钮的点击信号到槽函数
        btn_add.clicked.connect(partial(self.addRow, None))
        btn_remove.clicked.connect(self.removeRow)
        btn_clear.clicked.connect(self.clearRows)
        btn_import.clicked.connect(self.importRows)

        # 创建按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_import)

        # 添加表格和按钮布局到主布局
        main_layout.addWidget(self.table_widget)
        main_layout.addLayout(btn_layout)

        # 创建确认和取消按钮
        btn_confirm = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_APPLY))
        btn_cancel = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CANCEL))

        # 连接确认和取消按钮的点击信号到槽函数
        btn_confirm.clicked.connect(self.onApply)
        btn_cancel.clicked.connect(self.onCancel)

        # 创建确认和取消按钮布局
        action_layout = QHBoxLayout()
        action_layout.addWidget(btn_confirm)
        action_layout.addWidget(btn_cancel)

        # 添加确认和取消按钮布局到主布局
        main_layout.addLayout(action_layout)

        # 加载已保存的batch info
        if self._default_batches_value is not None:
            for batch_value in self._default_batches_value:
                self.addRow(batch_value)

    def getValueWidget(self, value=None):
        parm_ui = None
        parm_meta = self._parm_meta
        parm_type = parm_meta.getData(HouParamMetaEnum.TYPE)
        parm_value = parm_meta.getData(HouParamMetaEnum.VALUE)
        parm_name = parm_meta.getData(HouParamMetaEnum.NAME)
        parm_label = parm_meta.getData(HouParamMetaEnum.LABEL)
        parm_range = parm_meta.getData(HouParamMetaEnum.VALUE_RANGE)
        parm_combox = parm_meta.getData(HouParamMetaEnum.COMBOX_DEFINE)

        if parm_type == HouParamTypeEnum.BUTTON:
            parm_ui = QCheckBox()
            parm_ui.setChecked(True if value is None else value)
            parm_ui.setToolTip(getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_BUTTON_TOOLTIP))

        elif parm_type == HouParamTypeEnum.TOGGLE:
            parm_ui = QCheckBox()
            parm_ui.setChecked(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.COLOR:
            use_alpha = True if len(parm_value) == 4 else False
            parm_ui = QColorSelector(use_alpha=use_alpha, use_color01=True)
            parm_ui.setValue(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.STRING:
            parm_ui = QLineEdit()
            parm_ui.setText(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.FILE_STRING:
            parm_ui = QFileString()
            parm_ui.setText(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.FLOAT:
            parm_ui = QFloatSlider(Qt.Horizontal)
            parm_ui.setRange(parm_range[0], parm_range[1])
            parm_ui.setValue(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.FLOAT_ARRAY:
            array_len = len(parm_value)
            parm_ui = QFloatVectorSpinBox(vector_length=array_len)
            if parm_range is not None:
                parm_ui.setRange(parm_range[0], parm_range[1])
            parm_ui.setValue(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.INT:
            parm_ui = QIntegerSlider(Qt.Horizontal)
            parm_ui.setRange(parm_range[0], parm_range[1])
            parm_ui.setValue(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.INT_ARRAY:
            array_len = len(parm_value)
            parm_ui = QIntVectorSpinBox(vector_length=array_len)
            if parm_range is not None:
                parm_ui.setRange(parm_range[0], parm_range[1])
            parm_ui.setValue(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.COMBOX:
            parm_ui = QComboBox()
            items = parm_combox.items
            labels = parm_combox.labels
            parm_ui.addItems(labels)
            parm_ui.setCurrentIndex(parm_value if value is None else value)

        elif parm_type == HouParamTypeEnum.RAMP:
            parm_ui = QRampWidget()
            parm_ui.ramp_widget.clearPoints()
            points = zip(parm_value["keys"], parm_value["values"]) if value is None else zip(value["keys"], value["values"])
            for point in points:
                parm_ui.ramp_widget.addPointFromPos(*point)

            basis = parm_value["basis"][0] if value is None else value["basis"][0]
            parm_ui.setInterpolationModeFromBasis(basis)

        return parm_ui

    def getFirstColumnItem(self, row_count):
        default_palette = self.table_widget.palette()
        default_color = default_palette.color(QPalette.Base)
        even_row_color = default_color.lighter(300)
        colors = [default_color, even_row_color]

        first_column_item = QTableWidgetItem(str(row_count + 1))
        first_column_item.setTextAlignment(Qt.AlignCenter)
        # first_column_item.setBackgroundColor(colors[row_count % 2])

        return first_column_item

    def getSecondColumnItem(self, value=None):
        value_widget = self.getValueWidget(value=value)
        return value_widget

    def addRow(self, value=None):
        row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(row_count)

        # 第一列
        first_column_item = self.getFirstColumnItem(row_count)
        self.table_widget.setItem(row_count, 0, first_column_item)

        # 第二列
        second_column_item = self.getSecondColumnItem(value=value)
        self.table_widget.setCellWidget(row_count, 1, second_column_item)

        # 设置行高
        original_height = self.table_widget.rowHeight(row_count - 1)
        new_height = original_height * 1.5
        if self._parm_meta.getData(HouParamMetaEnum.TYPE) == HouParamTypeEnum.RAMP:
            new_height = 100

        self.table_widget.setRowHeight(row_count - 1, new_height)
        self.table_widget.setRowHeight(row_count, new_height)

    def removeRow(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, getLocalizationStr(LANG_STR_ENUM.UI_WARNING), getLocalizationStr(LANG_STR_ENUM.UI_BATCHPANEL_SELECT_REMOVE_ROW))
            return
        for item in selected_items:
            self.table_widget.removeRow(item.row())

        self.updateBatchNumbers()

    def updateBatchNumbers(self):
        row_count = self.table_widget.rowCount()
        for row in range(row_count):
            first_column_item = self.getFirstColumnItem(row)
            self.table_widget.setItem(row, 0, first_column_item)

    def clearRows(self):
        self.table_widget.setRowCount(0)

    def importRows(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, '导入文件', '', 'CSV Files (*.csv);;All Files (*)')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    batch, attr = line.strip().split(',')
                    row_count = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_count)
                    self.table_widget.setItem(row_count, 0, QTableWidgetItem(batch))
                    self.table_widget.setItem(row_count, 1, QTableWidgetItem(attr))

    def gatherBatchValues(self):
        batches_value = []

        parm_type = self._parm_meta.getData(HouParamMetaEnum.TYPE)
        for row in range(self.table_widget.rowCount()):
            widget = self.table_widget.cellWidget(row, 1)
            parm_value = None
            if widget:
                if parm_type == HouParamTypeEnum.BUTTON or parm_type == HouParamTypeEnum.TOGGLE:
                    parm_value = widget.isChecked()
                elif (parm_type == HouParamTypeEnum.FLOAT or parm_type == HouParamTypeEnum.INT or parm_type == HouParamTypeEnum.FLOAT_ARRAY or parm_type == HouParamTypeEnum.INT_ARRAY) or parm_type == HouParamTypeEnum.COLOR:
                    parm_value = widget.value()
                elif parm_type == HouParamTypeEnum.COMBOX:
                    parm_value = widget.currentIndex()
                elif parm_type == HouParamTypeEnum.STRING or parm_type == HouParamTypeEnum.FILE_STRING:
                    parm_value = widget.text()
                elif parm_type == HouParamTypeEnum.RAMP:
                    parm_value = widget.ramp_widget.getHouRampParms()
            batches_value.append(parm_value)
        print(batches_value)
        return batches_value

    def onApply(self):
        parm_name = self._parm_meta.getData(HouParamMetaEnum.NAME)
        self.on_save_batch_info.emit(parm_name, self.gatherBatchValues())
        self.close()

    def onCancel(self):
        self.close()
