from PyQt5.QtWidgets import QMessageBox, QDialog, QCheckBox, QDialogButtonBox, QFormLayout, QLabel

# https://stackoverflow.com/questions/56019273/how-can-i-get-more-input-text-in-pyqt5-inputdialog
# TODO at least has to be checked to be able to click OK
class SplitInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Split selection")
        self.bass_checkbox = QCheckBox()
        self.drums_checkbox = QCheckBox()
        self.guitars_checkbox = QCheckBox()
        self.vocals_checkbox = QCheckBox()
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


def showWarningDialog(title, message):
    dialog = QMessageBox()
    dialog.setModal(True)
    dialog.setIcon(QMessageBox.Information)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.exec()
