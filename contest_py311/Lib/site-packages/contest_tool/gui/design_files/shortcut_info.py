
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_table_widget_dialog(object):
    def setupUi(self, table_widget_dialog):
        table_widget_dialog.setObjectName("table_widget_dialog")
        table_widget_dialog.resize(423, 394)
        self.gridLayout = QtWidgets.QGridLayout(table_widget_dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.table_widget = QtWidgets.QTableWidget(table_widget_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_widget.sizePolicy().hasHeightForWidth())
        self.table_widget.setSizePolicy(sizePolicy)
        self.table_widget.setObjectName("table_widget")
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        self.verticalLayout.addWidget(self.table_widget)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        self.retranslateUi(table_widget_dialog)
        QtCore.QMetaObject.connectSlotsByName(table_widget_dialog)

    def retranslateUi(self, table_widget_dialog):
        _translate = QtCore.QCoreApplication.translate
        table_widget_dialog.setWindowTitle(_translate("table_widget_dialog", "Short Cuts"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    table_widget_dialog = QtWidgets.QDialog()
    ui = Ui_table_widget_dialog()
    ui.setupUi(table_widget_dialog)
    table_widget_dialog.show()
    sys.exit(app.exec_())
