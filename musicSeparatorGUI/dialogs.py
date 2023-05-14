from PyQt5.QtWidgets import QMessageBox, QDialog, QCheckBox, QDialogButtonBox, QFormLayout, QLabel, QToolButton, \
    QLineEdit, QFileDialog, QGridLayout, QVBoxLayout, QComboBox
from PyQt5.QtCore import QCoreApplication, QMetaObject
from utils import load_json_file
import torch

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           dialogs.py
    Description:    Dialog for split selection, settings selection and a warning dialog
"""


class SplitInputDialog(QDialog):
    """
    Dialog allowing user to choose which instruments to separate
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Split selection")
        self.bass_checkbox = QCheckBox()
        self.bass_checkbox.setChecked(True)
        self.drums_checkbox = QCheckBox()
        self.drums_checkbox.setChecked(True)
        self.guitars_checkbox = QCheckBox()
        self.guitars_checkbox.setChecked(True)
        self.vocals_checkbox = QCheckBox()
        self.vocals_checkbox.setChecked(True)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow(QLabel("Select which tracks to separate:"))
        layout.addRow("Bass", self.bass_checkbox)
        layout.addRow("Drums", self.drums_checkbox)
        layout.addRow("Guitars", self.guitars_checkbox)
        layout.addRow("Vocals", self.vocals_checkbox)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return {"bass": self.bass_checkbox.isChecked(), "drums": self.drums_checkbox.isChecked(),
                "guitars": self.guitars_checkbox.isChecked(), "vocals": self.vocals_checkbox.isChecked()}


class SettingsDialog(QDialog):
    """
    Dialog with settings related to separation process
    """

    xps_name_dict = {"195c4583": "Remix + Medley (24/6)", "442d1ed0": "Remix + Medley (28/6)",
                     "0b6894ef": "Remix (12/3)", "9af80a6a": "Medley (12/3)", "af9a0947": "Remix + Medley (12/3)"}
    name_xps_dict = {"Remix + Medley (24/6)": "195c4583", "Remix + Medley (28/6)": "442d1ed0",
                     "Remix (12/3)": "0b6894ef", "Medley (12/3)": "9af80a6a", "Remix + Medley (12/3)": "af9a0947"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        self.show()

    def _open_file_dialog(self, lineEdit):
        directory = str(QFileDialog.getExistingDirectory())
        lineEdit.setText('{}'.format(directory))

    def retranslateUI(self, fileDialog, openButton, dialogue: str, d: str):
        _translate = QCoreApplication.translate
        fileDialog.setWindowTitle(_translate(dialogue, d))
        openButton.setText(_translate(dialogue, "..."))

    def setupUI(self):
        current_settings = load_json_file("./conf/separation_config.json")

        self.setWindowTitle("Separation settings")
        self.setMinimumSize(400, 180)

        # Choosing folder where models are located
        ModelsFolderDialog = QDialog()
        self.buttonOpenDialog = QToolButton(ModelsFolderDialog)
        self.folderLineEdit = QLineEdit(current_settings["repo"])
        self.folderLineEdit.setEnabled(False)

        self.buttonOpenDialog.clicked.connect(lambda: (self._open_file_dialog(self.folderLineEdit)))

        self.retranslateUI(ModelsFolderDialog, self.buttonOpenDialog, "TestQFileDialog", "data")
        QMetaObject.connectSlotsByName(ModelsFolderDialog)

        # Choosing device - CPU or GPU
        self.deviceComboBox = QComboBox()
        self.deviceComboBox.addItem('cpu')

        if torch.cuda.is_available():
            self.deviceComboBox.addItem('cuda')
            if current_settings["device"] == "cpu":
                self.deviceComboBox.setCurrentIndex(0)
            else:
                self.deviceComboBox.setCurrentIndex(1)

        # Choosing model signature
        self.modelNameComboBox = QComboBox()
        for key, val in self.xps_name_dict.items():
            self.modelNameComboBox.addItem(val)

        self.modelNameComboBox.setCurrentText(self.xps_name_dict[current_settings["name"]])

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Device:"), 0, 0)
        grid_layout.addWidget(self.deviceComboBox, 0, 1)
        grid_layout.addWidget(QLabel("Models folder:"), 1, 0)
        grid_layout.addWidget(self.folderLineEdit, 1, 1)
        grid_layout.addWidget(self.buttonOpenDialog, 1, 2)
        grid_layout.addWidget(QLabel("Model name:"), 2, 0)
        grid_layout.addWidget(self.modelNameComboBox, 2, 1)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        ve_box = QVBoxLayout()
        ve_box.addLayout(grid_layout)
        ve_box.addWidget(buttonBox)

        self.setLayout(ve_box)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return {"device": self.deviceComboBox.currentText(), "repo": self.folderLineEdit.text(),
                "name": self.name_xps_dict[self.modelNameComboBox.currentText()], "mp3": True}


def showWarningDialog(title, message):
    """
    Creates a popup dialog with specified title and message
    """
    dialog = QMessageBox()
    dialog.setModal(True)
    dialog.setIcon(QMessageBox.Information)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.exec()
