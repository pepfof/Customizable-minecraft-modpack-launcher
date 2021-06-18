from requests import get
from os import remove, makedirs, mkdir
from os.path import exists, join, abspath
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QFileDialog, QApplication
from getpass import getuser
from datetime import datetime
import Custom

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)


class Ui_Dialog(object):
    
    def setupUi(self, Dialog):
        Dialog.setObjectName(Custom.Updater_title)
        Dialog.setFixedSize(423, 311)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("icon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(310, 10, 101, 44))
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 252, 24))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 121, 16))
        self.label.setObjectName("label")
        self.dirselect = QtWidgets.QPushButton(Dialog)
        self.dirselect.setGeometry(QtCore.QRect(260, 30, 24, 24))
        self.dirselect.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.dirselect.setObjectName("dirselect")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(10, 95, 401, 186))
        self.textBrowser.setObjectName("textBrowser")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 70, 401, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.pushButton.clicked.connect(self.runLongTask)
        self.dirselect.clicked.connect(self.dirselecting)
        self.aboutbutton = QtWidgets.QPushButton(Dialog)
        self.aboutbutton.setGeometry(QtCore.QRect(391, 285, 20, 20))
        self.aboutbutton.setObjectName("pushButton")
        self.aboutbutton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.log = " "
        
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", Custom.Updater_title))
        self.aboutbutton.setToolTip(_translate("Dialog", "About"))
        self.label.setText(_translate("Dialog", "Minecraft Directory:"))
        self.pushButton.setToolTip(_translate("Dialog", "Shift+click to force download all"))
        self.pushButton.setText(_translate("Dialog", "Update!"))
        self.aboutbutton.setText(_translate("Dialog", "?"))
        self.dirselect.setText(_translate("Dialog", "..."))
    
    def updateLog(self, input):
        original = self.log
        self.log = datetime.now().strftime("[%H:%M:%S] ") + input + "\n" + original
        with open("./updater_latest.log", 'w') as file:
            file.write(self.log)
        self.textBrowser.setPlainText(self.log)

    def runLongTask(self):  
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.pushButton.connect(self.pushButton.setEnabled)
        self.worker.lineEdit_set.connect(self.lineEdit.setEnabled)
        self.worker.dirselect.connect(self.dirselect.setEnabled)
        self.worker.progressBar.connect(self.progressBar.setProperty)
        self.worker.logging.connect(self.updateLog)      
        self.thread.start()

    def dirselecting(self):
         self.lineEdit.setText(QFileDialog.getExistingDirectory(None, "Open Directory", self.lineEdit.text(), QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

class Worker(QObject):
    
    finished = pyqtSignal()
    pushButton = pyqtSignal(int)
    lineEdit_set = pyqtSignal(int)
    dirselect = pyqtSignal(int)
    progressBar = pyqtSignal(str, int)
    logging = pyqtSignal(str)
    
    def progressbar(self, counter, all):
        self.progressBar.emit("maximum", all)
        self.progressBar.emit("value", counter)
        return 0

    def run(self):
        self.dirselect.emit(0)
        self.lineEdit_set.emit(0)
        self.pushButton.emit(0)
        global check
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            force = True
        else:
            force = False

        if(ui.lineEdit.text() == ''):
            self.logging.emit(f'No directory selected!')
            self.finished.emit()
            return 0
        
        fpath=ui.lineEdit.text()

        path_to_txtn = join(path, 'dir.txt')
        with open(path_to_txtn, 'w') as file:
                file.write(ui.lineEdit.text())
        if(force):
            if(not check):
                self.logging.emit(f'Warning!\nForce redownloading will\ndelete all previously downloaded content!\nShift-click "Update!" again to continue.\n\n\n\n\n')
                check = True
                self.dirselect.emit(1)
                self.lineEdit_set.emit(1)
                self.pushButton.emit(1)
                self.finished.emit()
                return 0
            if(check):
                check = False

        req = get(Custom.Source_URL+"mine.txt")            
        files_new = set(req.text.split('\n'))
        files_new.remove('')
        files_new = {a[1:].replace('\\', '/') for a in files_new}
        if(force):
            for i in files_new:
                if(exists(join(fpath,i))):
                    remove(join(fpath,i))
        self.logging.emit(f'Checking for updates...')        
        req = get(Custom.Source_URL+"/dirs.txt")
        all_dirs = {i[1:].replace('\\', '/') for i in req.text.split('\n') if not exists(join(fpath,i[1:]))}
        req = get(Custom.Source_URL+"remv.txt")
        files_delete = {i[1:].replace('\\', '/') for i in req.text.split('\n') if i != '' and exists(join(fpath,i[1:]))}
        for i in files_delete:
            remove(join(fpath,i))
        for i in all_dirs:
            if(not exists(join(fpath,i))):
                makedirs(join(fpath,i))
        if(not force):
            files_new = {i for i in files_new if not exists(join(fpath,i))}
        counter = 0
        for i in files_new:
            with open(join(fpath,i), 'wb') as f:
                ufr = get(f"{Custom.Source_URL}{i}")
                f.write(ufr.content)
                counter += 1
                self.progressbar(counter, len(files_new))
                self.logging.emit(f'Download {i}')

        self.logging.emit(f"Done updating {Custom.Modpack_name}!")
        self.progressbar(1,0)
        self.dirselect.emit(1)
        self.lineEdit_set.emit(1)
        self.pushButton.emit(1)
        self.finished.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    path = './'
    check = False
    if(not exists(path)):
        mkdir(path)
    
    default_name = f'C:\\Users\\{getuser()}\\AppData\\Roaming\\.minecraft'
    path_to_txtn = join(path, 'dir.txt')
    if(exists(path_to_txtn)):
        with open(path_to_txtn, 'r') as file:
            default_name = file.readline()
    ui.lineEdit.setText(default_name)

    sys.exit(app.exec_())
