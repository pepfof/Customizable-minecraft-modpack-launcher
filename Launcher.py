from minecraft_launcher_lib.forge import install_forge_version, install_forge_old_version
from minecraft_launcher_lib.utils import get_installed_versions
from minecraft_launcher_lib.command import get_minecraft_command
from subprocess import call
from requests import get
from os import remove, mkdir, makedirs
import subprocess
from os.path import exists, join, abspath, expanduser
from shutil import rmtree, move
import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRect, Qt, QCoreApplication, QMetaObject
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QProgressBar, QTextBrowser, QApplication, QDialog, QMessageBox
from time import sleep
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
        Dialog.setObjectName(Custom.Launcher_title)
        Dialog.setFixedSize(423, 320)
        icon = QIcon()
        icon.addPixmap(QPixmap(resource_path("icon.ico")),
                       QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.lineEdit = QLineEdit(Dialog)
        self.lineEdit.setGeometry(QRect(10, 30, 281, 24))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QRect(310, 30, 101, 24))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QLabel(Dialog)
        self.label.setGeometry(QRect(10, 10, 71, 16))
        self.label.setObjectName("label")
        self.label_2 = QLabel(Dialog)
        self.label_2.setGeometry(QRect(310, 10, 101, 16))
        self.label_2.setAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.progressBar = QProgressBar(Dialog)
        self.progressBar.setGeometry(QRect(10, 86, 281, 16))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setGeometry(QRect(310, 63, 101, 39))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton.clicked.connect(self.runLongTask)
        self.aboutbutton = QPushButton(Dialog)
        self.aboutbutton.setGeometry(QRect(391, 294, 20, 20))
        self.aboutbutton.setObjectName("pushButton")
        self.aboutbutton.setCursor(QCursor(Qt.PointingHandCursor))
        self.aboutbutton.clicked.connect(self.knopka)
        self.textBrowser = QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QRect(10, 115, 401, 175))
        self.textBrowser.setObjectName("textBrowser")
        self.label_3 = QLabel(Dialog)
        self.label_3.setGeometry(QRect(10, 60, 281, 21))
        self.label_3.setTextFormat(Qt.MarkdownText)
        self.label_3.setScaledContents(False)
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Dialog)
        QMetaObject.connectSlotsByName(Dialog)

        self.log = " "

    def knopka(self):
        icon = QIcon()
        icon.addPixmap(QPixmap(resource_path("icon.ico")),
                       QIcon.Normal, QIcon.Off)
        msgBox = QMessageBox()
        msgBox.setText(f'''<a href = "https://github.com/pepfof/Customizable-minecraft-modpack-launcher"><h2>Customizable minecraft modpack launcher</h2></a> by bopchik and pepfof<br>licensed under the <a href = "https://github.com/pepfof/Customizable-minecraft-modpack-launcher/blob/main/LICENSE">BSD 2-clause license</a><br><br>
        Written using <a href = "https://gitlab.com/JakobDev/minecraft-launcher-lib">Minecraft Launcher Lib by JakobDev</a><br> licensed under the <a href = "https://gitlab.com/JakobDev/minecraft-launcher-lib/-/blob/master/LICENSE">BSD 2-clause license</a><br><br>
        Modpack:<br>
        <a href = "{Custom.Modpack_url}">{Custom.Modpack_name} by {Custom.Modpack_author}</a><br>
        licensed under the <a href = "{Custom.Modpack_license_url}">{Custom.Modpack_license_name}</a>''')

        msgBox.setWindowTitle("About")
        msgBox.setWindowIcon(icon)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", Custom.Launcher_title))
        self.label.setText(_translate("Dialog", "Username:"))
        self.lineEdit_2.setInputMask(_translate("Dialog", "00000"))
        self.pushButton.setToolTip(_translate(
            "Dialog", "Shift+click to force re-download all"))
        self.aboutbutton.setToolTip(_translate("Dialog", "About"))
        self.label_2.setText(_translate("Dialog", "Max. Mem. (MB)"))
        self.pushButton.setText(_translate("Dialog", "Play!"))
        self.aboutbutton.setText(_translate("Dialog", "?"))
        self.label_3.setText(_translate("Dialog", "Ready!"))

    def updateLog(self, input):
        original = self.log
        self.log = datetime.now().strftime("[%H:%M:%S] ") + input + "\n" + original
        with open(join('.',"launcher_latest.log"), 'w') as file:
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
        self.worker.label_1.connect(self.label.setText)
        self.worker.label_2.connect(self.label_2.setText)
        self.worker.label_3.connect(self.label_3.setText)
        self.worker.pushButton.connect(self.pushButton.setEnabled)
        self.worker.lineEdit_set.connect(self.lineEdit.setEnabled)
        self.worker.lineEdit2_set.connect(self.lineEdit_2.setEnabled)
        self.worker.progressBar.connect(self.progressBar.setProperty)
        self.worker.logging.connect(self.updateLog)
        self.thread.start()


def maximum(max_value, value):
    max_value[0] = value


class Worker(QObject):

    logging = pyqtSignal(str)
    finished = pyqtSignal()
    label_1 = pyqtSignal(str)
    label_2 = pyqtSignal(str)
    label_3 = pyqtSignal(str)
    pushButton = pyqtSignal(int)
    lineEdit_set = pyqtSignal(int)
    lineEdit2_set = pyqtSignal(int)
    progressBar = pyqtSignal(str, int)

    def progressbar(self, counter, all, up_to_date):
        if(up_to_date):
            self.progressBar.emit("maximum", 1)
            self.progressBar.emit("value", 1)
        else:
            self.progressBar.emit("maximum", all)
            self.progressBar.emit("value", counter)
        return 0

    def reportTwice(self, input):
        self.label_3.emit(input)
        self.logging.emit(input)

    def run(self):
        global check
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            force = True
        else:
            force = False
        if(ui.lineEdit.text() == ''):
            self.label_3.emit(f'Please input username!')
            self.finished.emit()
            return 0
        elif(ui.lineEdit_2.text() == ''):
            self.label_3.emit(
                f'Please input maximum memory! (min. 2048 recommended)')
            self.finished.emit()
            return 0

        if(force):
            if(not check):
                self.logging.emit(
                    f'Warning!\nForce re-downloading will also\ndelete all minecraft settings and config!\nShift-click "Update!" again to continue.\n\n\n\n\n')
                check = True
                self.lineEdit_set.emit(1)
                self.pushButton.emit(1)
                self.finished.emit()
                return 0
            if(check):
                check = False
        
        up_to_date = False

        self.pushButton.emit(0)
        self.lineEdit2_set.emit(0)
        self.lineEdit_set.emit(0)

        path = join(expanduser('~'), Custom.Launcher_folder_path)

        maxmem = f"-Xmx{int(ui.lineEdit_2.text())}M"
        jargs = [maxmem]
        if(Custom.Server_Autoconnect == 1):
            options = {
                "username": ui.lineEdit.text(),
                "uuid": "0",
                "token": "0",
                "jvmArguments": jargs,
                "server": Custom.Server_IP,
                "port": Custom.Server_port,
                "launcherName": Custom.Launcher_title
            }
        else:
            options = {
                "username": ui.lineEdit.text(),
                "uuid": "0",
                "token": "0",
                "jvmArguments": jargs,
                "launcherName": Custom.Launcher_title
            }

        path_to_txtr = join(path, 'ram.txt')
        with open(path_to_txtr, 'w') as file:
            file.write(ui.lineEdit_2.text())
        path_to_txtn = join(path, 'name.txt')
        with open(path_to_txtn, 'w') as file:
            file.write(ui.lineEdit.text())

        max_value = [0]

        callback = {
            "setStatus": lambda text: self.reportTwice(text),
            "setProgress": lambda value: self.progressbar(value, max_value[0], up_to_date),
            "setMax": lambda value: maximum(max_value, value)
        }

        if(force):
            if(not exists(join('.', 'Temp_folder'))):
                mkdir(join('.', 'Temp_folder'))
            req = get(Custom.Source_URL+"save.txt")
            files_save = set(req.text.split('\n'))
            files_save.remove('')
            if(len(files_save)):
                files_save = {a[1:] for a in files_save}
                for i in files_save:
                    if(exists(join(path, i))):
                        move(join(path, i),join('.', 'Temp_folder', i))

        if(Custom.Is_below_1_13):
            if(force):
                if(exists(path)):
                    rmtree(path)
                self.reportTwice(f'Downloading and installing minecraft forge...')
                install_forge_old_version(
                    Custom.Forge_version, path, callback=callback)
            else:
                if(not exists(join(path, 'versions', Custom.Forge_version_name, f'{Custom.Forge_version_name}.jar'))):
                    self.reportTwice(f'Downloading and installing minecraft forge...')
                    install_forge_old_version(
                        Custom.Forge_version, path, callback=callback)
        else:
            if(force):
                if(exists(path)):
                    rmtree(path)
                self.reportTwice(f'Downloading and installing minecraft forge...')
                install_forge_version(
                    Custom.Forge_version, path, callback=callback)
            else:
                if(not exists(join(path, 'versions', Custom.Forge_version_name, f'{Custom.Forge_version_name}.jar'))):
                    self.reportTwice(f'Downloading and installing minecraft forge...')
                    install_forge_version(
                        Custom.Forge_version, path, callback=callback)

        command = get_minecraft_command(
            Custom.Forge_version_name, path, options)

        self.reportTwice(f'Checking for {Custom.Modpack_name} updates...')

        req = get(Custom.Source_URL+"mine.txt")
        files_new = set(req.text.split('\n'))
        files_new.remove('')
        files_new = {a[1:].replace('\\', '/') for a in files_new}
        req = get(Custom.Source_URL+"dirs.txt")
        all_dirs = {i[1:].replace(
            '\\', '/') for i in req.text.split('\n') if not exists(join(path, i[1:]))}
        req = get(Custom.Source_URL+"remv.txt")
        files_delete = {i[1:].replace(
            '\\', '/') for i in req.text.split('\n') if i != '' and exists(join(path, i[1:]))}
        for i in files_delete:
            remove(join(path, i))
        for i in all_dirs:
            if(not exists(join(path, i))):
                makedirs(join(path, i))

        if(not force):
            files_new = {i for i in files_new if not exists(join(path, i))}

        if(files_delete == files_new):
            self.reportTwice('Already up to date!')
            up_to_date = True

        counter = 0

        for i in files_new:
            with open(join(path, i), 'wb') as f:
                ufr = get(f"{Custom.Source_URL}{i}")
                f.write(ufr.content)
                counter += 1
                self.progressbar(counter, len(files_new), up_to_date)
                if(not up_to_date):
                    self.reportTwice(f'Download {i}')

        if(force):
            if(len(files_save)):
                for i in files_save:
                    if(exists(join('.', 'Temp_folder', i))):
                        if(exists(join(path, i))):
                            remove(join(path, i))
                        move(join('.', 'Temp_folder', i), join(path, i))
                if(exists(join('.', 'Temp_folder'))):
                    rmtree(join('.', 'Temp_folder'))

        up_to_date = False
        self.reportTwice(Custom.Modpack_name + " launched!")
        self.progressbar(1, 0, up_to_date)
        call(command, cwd=path)
        self.pushButton.emit(1)
        self.lineEdit2_set.emit(1)
        self.lineEdit_set.emit(1)
        self.label_3.emit("Ready!")
        self.progressbar(0, 1, up_to_date)
        self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Dialog = QDialog(None, Qt.WindowSystemMenuHint |
                     Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    check = False
    path = join(expanduser('~'), Custom.Launcher_folder_path)
    if(not exists(path)):
        mkdir(path)

    default_ram = Custom.Min_Mem
    ram = ''
    path_to_txtr = join(path, 'ram.txt')
    if(exists(path_to_txtr)):
        with open(path_to_txtr, 'r') as file:
            default_ram = file.readline()
    ui.lineEdit_2.setText(default_ram)

    default_name = ''
    ram = ''
    path_to_txtn = join(path, 'name.txt')
    if(exists(path_to_txtn)):
        with open(path_to_txtn, 'r') as file:
            default_name = file.readline()
    ui.lineEdit.setText(default_name)

    sys.exit(app.exec_())
