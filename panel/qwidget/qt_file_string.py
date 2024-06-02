from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog
from PySide2.QtCore import Signal


class QFileString(QWidget):
    filePathEntered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        file_layout = QHBoxLayout()

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("File path will appear here")
        self.line_edit.editingFinished.connect(self.emit_file_path_entered)
        file_layout.addWidget(self.line_edit)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.open_file_dialog)
        file_layout.addWidget(self.browse_button)

        self.setLayout(file_layout)

    def setText(self, value):
        self.line_edit.setText(value)

    def text(self):
        return self.line_edit.text()

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_path:
            self.line_edit.setText(file_path)
            self.emit_file_path_entered()

    def emit_file_path_entered(self):
        file_path = self.line_edit.text()
        self.filePathEntered.emit(file_path)

    def get_file_path(self):
        return self.line_edit.text()

    def set_file_path(self, path):
        self.line_edit.setText(path)
        self.emit_file_path_entered()
