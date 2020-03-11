#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import ctypes
from pathlib import Path

import DICOM_Reader

# Import the core and GUI elements of Qt
from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QAction, QWidget, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QLabel, \
    QApplication, QFileDialog,QHBoxLayout

# to allow windows icon task bar
myappid = 'nath.app.LungBLine'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.mainGUI = MainGui(self)
        self.setCentralWidget(self.mainGUI)

        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle('Lung BLine')
        self.setWindowIcon(QIcon(resource_path("resource/steam-icon.png")))

        self.closeEvent = self.mainGUI.closeEvent  # close event is handled in mainGUI

        # menu action
        self.quitAction = QAction("&Quit", self)
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.setStatusTip('Quit Lung BLine')
        self.quitAction.triggered.connect(self.close)
        self.quitAction.setIcon(QIcon(resource_path("resource/close-icon.png")))

        self.aboutAction = QAction("&About", self)
        self.aboutAction.setShortcut("Ctrl+B")
        self.aboutAction.setStatusTip('About')
        self.aboutAction.triggered.connect(self.mainGUI.aboutPopUp)
        self.aboutAction.setIcon(QIcon(resource_path("resource/about-icon.png")))

        self.openAction = QAction("&Open Dicom file", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip('Open')
        self.openAction.triggered.connect(self.mainGUI.openFile)
        self.openAction.setIcon(QIcon(resource_path("resource/about-icon.png")))

        self.statusBar()

        # menu bar
        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('&Tools')

        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.aboutAction)
        fileMenu.addAction(self.quitAction)

        self.show()


class MainGui(QWidget):
    filePath = pyqtSignal(str)
    fileArray = pyqtSignal()

    def __init__(self, parent):
        super(MainGui, self).__init__(parent)

        # grid layout
        self.main_vlayout = QVBoxLayout(self)
        self.setLayout(self.main_vlayout)



        # button
        self.prevButton = QPushButton("Prev")
        self.prevButton.setDisabled(True)
        self.nextButton = QPushButton("Next")
        self.nextButton.setDisabled(True)

        # qlabel
        self.label_image = QLabel(self)
        self.label_index_image = QLabel(self)


        self.qcombobox_account = QComboBox()



        # signal
        self.filePath.connect(self.readDicomFile)
        self.fileArray.connect(self.display_image)
        self.prevButton.clicked.connect(self.prev_image)
        self.nextButton.clicked.connect(self.next_image)

        # horizontal layout for loading info and go back button
        self.hbox_info = QHBoxLayout()
        self.hbox_info.addWidget(self.prevButton)
        self.hbox_info.addWidget(self.label_index_image)
        self.hbox_info.addWidget(self.nextButton)

        # gui layout
        self.main_vlayout.addWidget(self.label_image)
        self.main_vlayout.addLayout(self.hbox_info)

        # model
        self.dicomFilePath = None
        self.imageArray = None
        self.image_index = 0

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open DICOM File",
                                                  directory=os.path.normpath(Path.home()), filter="*")
        if fileName:
            self.dicomFilePath = fileName
            self.filePath.emit(str(self.dicomFilePath))

    @pyqtSlot(str)
    def readDicomFile(self, dicom_filepath):
        reader = DICOM_Reader.DICOMReader(dicom_filepath, False)

        self.imageArray = reader.get_images_array()
        self.prevButton.setDisabled(False)
        self.nextButton.setDisabled(False)
        self.fileArray.emit()

    @pyqtSlot()
    def display_image(self, index=0):
        image = self.imageArray[index]

        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_Indexed8)
        pix = QPixmap(image)

        self.label_image.setPixmap(pix)
        self.label_index_image.setText(str(self.image_index) + "/" + str(self.imageArray.shape[0]))

    @pyqtSlot()
    def prev_image(self):
        if self.image_index > 0:
            self.image_index -=1
            self.label_index_image.setText(str(self.image_index)+"/"+str(self.imageArray.shape[0]))
            self.display_image(self.image_index)

    @pyqtSlot()
    def next_image(self):
        if self.image_index < self.imageArray.shape[0]:
            self.image_index += 1
            self.label_index_image.setText(str(self.image_index) + " / " + str(self.imageArray.shape[0]))
            self.display_image(self.image_index)

    def closeEvent(self, event):
        print("close event")
        print("closed")

    def noSteamPath(self):
        self.errorDialog("No Steam Path", "No Steam.exe path ! \nUse Tools->Change Steam path (Ctrl+C)")

    def noAccountsFound(self):
        self.errorDialog("No account(s) registered !", "No account(s) registered ! \nUse Tools->Add Account (Ctrl+A)")

    def errorDialog(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def aboutPopUp(self):
        mailLabel = QLabel("<a href='mailto:ponceau.nathanael@gmail.com'>ponceau.nathanael@gmail.com</a>")
        mailLabel.setOpenExternalLinks(True)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Steam Account Manager is created by : \n Nathanael Ponceau")
        msg.layout().addWidget(mailLabel)
        msg.setWindowTitle("About")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def resource_path(relative_path):
    '''
    Using this function to get the path of bundled resource into .exe with pyinstaller.
    ref:https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
    :param relative_path:
    :return:
    '''
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
