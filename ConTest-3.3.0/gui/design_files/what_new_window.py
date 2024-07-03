
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(650, 407)
        Dialog.setMinimumSize(QtCore.QSize(650, 0))
        Dialog.setSizeGripEnabled(False)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.cb_dont_show = QtWidgets.QCheckBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.cb_dont_show.setFont(font)
        self.cb_dont_show.setObjectName("cb_dont_show")
        self.gridLayout.addWidget(self.cb_dont_show, 0, 0, 1, 1)
        self.pb_close = QtWidgets.QPushButton(Dialog)
        self.pb_close.setObjectName("pb_close")
        self.gridLayout.addWidget(self.pb_close, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 1)
        self.pt_info = QtWidgets.QPlainTextEdit(Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pt_info.setFont(font)
        self.pt_info.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.pt_info.setReadOnly(True)
        self.pt_info.setObjectName("pt_info")
        self.gridLayout_2.addWidget(self.pt_info, 1, 0, 1, 1)
        self.release_more_details = QtWidgets.QLabel(Dialog)
        self.release_more_details.setText("")
        self.release_more_details.setObjectName("release_more_details")
        self.gridLayout_2.addWidget(self.release_more_details, 2, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Feature List [Release vx.x.x]"))
        self.label.setText(_translate("Dialog", "What\'s New?"))
        self.cb_dont_show.setText(_translate("Dialog", "  Don\'t show again"))
        self.pb_close.setText(_translate("Dialog", "OK"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
