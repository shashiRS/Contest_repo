
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_manual_verification(object):
    def setupUi(self, manual_verification):
        manual_verification.setObjectName("manual_verification")
        manual_verification.resize(754, 282)
        manual_verification.setWindowTitle("")
        self.gridLayout = QtWidgets.QGridLayout(manual_verification)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(manual_verification)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.user_question = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.user_question.setFont(font)
        self.user_question.setText("")
        self.user_question.setObjectName("user_question")
        self.gridLayout_2.addWidget(self.user_question, 0, 0, 1, 2)
        self.user_explanation = QtWidgets.QPlainTextEdit(self.groupBox)
        self.user_explanation.setObjectName("user_explanation")
        self.gridLayout_2.addWidget(self.user_explanation, 1, 0, 1, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.timer_manual_verify = QtWidgets.QLCDNumber(self.groupBox_2)
        self.timer_manual_verify.setObjectName("timer_manual_verify")
        self.horizontalLayout.addWidget(self.timer_manual_verify)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.yes_button = QtWidgets.QPushButton(self.groupBox_2)
        self.yes_button.setObjectName("yes_button")
        self.horizontalLayout.addWidget(self.yes_button)
        self.no_button = QtWidgets.QPushButton(self.groupBox_2)
        self.no_button.setObjectName("no_button")
        self.horizontalLayout.addWidget(self.no_button)
        self.gridLayout_2.addWidget(self.groupBox_2, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 2)

        self.retranslateUi(manual_verification)
        QtCore.QMetaObject.connectSlotsByName(manual_verification)

    def retranslateUi(self, manual_verification):
        _translate = QtCore.QCoreApplication.translate
        self.user_question.setToolTip(_translate("manual_verification", "<html><head/><body><p>Manual Verification User Query</p></body></html>"))
        self.user_explanation.setToolTip(_translate("manual_verification", "<html><head/><body><p>Please enter here optional explanation or comments based on manual verification of the query.</p><p>The explanation or comments will be provided as return value of the verification API.</p></body></html>"))
        self.user_explanation.setPlaceholderText(_translate("manual_verification", "Enter any explanation here ... (optional) "))
        self.timer_manual_verify.setToolTip(_translate("manual_verification", "<html><head/><body><p>Count down timer running until verdict (Yes/No) is provided.</p></body></html>"))
        self.yes_button.setToolTip(_translate("manual_verification", "<html><head/><body><p>Press &quot;Yes&quot; if query is verified.</p></body></html>"))
        self.yes_button.setText(_translate("manual_verification", "Yes"))
        self.no_button.setToolTip(_translate("manual_verification", "<html><head/><body><p>Press &quot;No&quot; if query is not verified.</p></body></html>"))
        self.no_button.setText(_translate("manual_verification", "No"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    manual_verification = QtWidgets.QDialog()
    ui = Ui_manual_verification()
    ui.setupUi(manual_verification)
    manual_verification.show()
    sys.exit(app.exec_())
