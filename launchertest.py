from minecraft_launcher_lib.forge import install_forge_version
from minecraft_launcher_lib.utils import get_installed_versions
from minecraft_launcher_lib.command import get_minecraft_command
from subprocess import call
from requests import get
from os import remove, makedirs, walk
from os.path import exists, join, basename, abspath, expanduser
from shutil import rmtree
from sys import argv
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
import time

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Memcraft launcher")
        Dialog.resize(426, 117)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./Downloads/briefcase_business_bag_icon_188751.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 281, 24))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(310, 30, 101, 24))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(310, 10, 101, 16))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 86, 281, 16))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(310, 63, 101, 39))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushButton.clicked.connect(on_button_clicked)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 60, 281, 21))
        self.label_3.setTextFormat(QtCore.Qt.MarkdownText)
        self.label_3.setScaledContents(False)
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Memcraft Launcher"))
        self.label.setText(_translate("Dialog", "Username:"))
        self.lineEdit_2.setInputMask(_translate("Dialog", "00000"))
        self.pushButton.setToolTip(_translate("Dialog", "Shift+click to force download all"))
        self.label_2.setText(_translate("Dialog", "Max. Mem. (MB)"))
        self.pushButton.setText(_translate("Dialog", "Play!"))
        self.label_3.setText(_translate("Dialog", "Ready!"))


def maximum(max_value, value):
    max_value[0] = value

def on_button_clicked():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    if modifiers == QtCore.Qt.ShiftModifier:
        run('-d')
    else:
        run('')



def progressbar(counter, all):
    ui.progressBar.setProperty("maximum", all)
    ui.progressBar.setProperty("value", counter)
    return 0

def run(args):
    if(ui.lineEdit.text()==''):
        ui.label_3.setText(f'Please input username!')
        return 0
    if(ui.lineEdit_2.text()==''):
        ui.label_3.setText(f'Please input maximum memory! (min. 2048 recommended)')
        return 0
    ui.pushButton.setEnabled(0)
    ui.lineEdit_2.setEnabled(0)
    ui.lineEdit.setEnabled(0)
    path = join(expanduser('~'), '.memcraft')
    maxmem=f"-Xmx{int(ui.lineEdit_2.text())}M"
    jargs = [maxmem]
    options = {
        "username": ui.lineEdit.text(),
        "uuid": "0",
        "token": "0",
        "jvmArguments": jargs,
        "server": "217.107.197.90",
        "port":"25565",
        "launcherName": "Memcraft"
    }

    path_to_txtr = join(path, 'ram.txt')
    with open(path_to_txtr, 'w') as file:
            file.write(ui.lineEdit_2.text())
    path_to_txtn = join(path, 'name.txt')
    with open(path_to_txtn, 'w') as file:
            file.write(ui.lineEdit.text())

    ui.label_3.setText(f'Getting Files...')

    max_value = [0]

    callback = {
        "setStatus": lambda text: ui.label_3.setText(text),
        "setProgress": lambda value: progressbar(value, max_value[0]),
        "setMax": lambda value: maximum(max_value, value)
    }

    if('-d' not in args):
        try:
            if(not {'id': '1.12.2-forge-14.23.5.2855', 'type': 'release'} in get_installed_versions(path)):
                install_forge_version("1.12.2-14.23.5.2855", path, callback=callback)
        except:
            install_forge_version("1.12.2-14.23.5.2855", path, callback=callback)
    else:
        install_forge_version("1.12.2-14.23.5.2855", path, callback=callback)

    ui.label_3.setText(f'Updating Mods...')

    command = get_minecraft_command("1.12.2-forge-14.23.5.2855", path, options)

    dirs = ['mods', 'config']
    if('-d' in args):
        for i in dirs:
            if(exists(join(path,i))):
                rmtree(join(path,i))
    req = get("https://pepfof.com/minecraft/mine.txt")
    files_new = set(req.text.split('\n'))
    files_new.remove('')
    files_new = {a[1:].replace('\\', '/') for a in files_new}
    req = get("https://pepfof.com/minecraft/dirs.txt")
    all_dirs = {i[1:].replace('\\', '/') for i in req.text.split('\n') if not exists(join(path,i[1:]))}
    req = get("https://pepfof.com/minecraft/remv.txt")
    files_delete = {i[1:].replace('\\', '/') for i in req.text.split('\n') if i != '' and exists(join(path,i[1:]))}
    for i in files_delete:
        remove(join(path,i))
    for i in all_dirs:
        if(not exists(join(path,i))):
            makedirs(join(path,i))
    if('-d' not in args):
        files_new = {i for i in files_new if not exists(join(path,i))}
    counter = 0
    for i in files_new:
        with open(join(path,i), 'wb') as f:
            ufr = get(f"https://pepfof.com/minecraft/{i}")
            f.write(ufr.content)
            counter += 1
            progressbar(counter, len(files_new))
            ui.label_3.setText(f'Download {i}')

    ui.label_3.setText("Memcraft launched!")
    progressbar(1,0)
    time.sleep(1)
#Start Minecraft
    call(command, cwd=path)
    time.sleep(1)
    ui.pushButton.setEnabled(1)
    ui.lineEdit_2.setEnabled(1)
    ui.lineEdit.setEnabled(1)
    ui.label_3.setText("Ready!")
    progressbar(0,1)
    return 0

if __name__ == "__main__":
    import sys



    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    path = join(expanduser('~'), '.memcraft/')
    if(not exists(path)):
        makedirs(path)

    default_ram = '2048'
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


