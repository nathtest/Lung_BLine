#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import copy
from pathlib import Path

from Model import DICOMReader
from Model.ComputeBlackWhitePercent import ComputeBlackWhitePercent
from View import QLabelSelectable
from Model.RunAlgorithms import RunAlgorithms

# Import the core and GUI elements of Qt
from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot, QModelIndex
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QAction, QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel, \
    QApplication, QFileDialog, QHBoxLayout, QCheckBox, QGroupBox, QTreeWidget, QFileSystemModel, QTreeView

# to allow windows icon task bar
myappid = 'nath.app.LungBLine'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class MainWindow(QMainWindow):
    """
    This class contain the menu action and parameter for the main window.
    Also it contain the main widget to be display inside the main window.
    """

    def __init__(self):
        super().__init__()

        self.mainGUI = MainGui(self)
        self.setCentralWidget(self.mainGUI)

        self.setMinimumSize(QSize(1000, 600))
        self.setMaximumSize(QSize(1400, 800))
        self.setWindowTitle('Lung BLine')
        self.setWindowIcon(QIcon(resource_path("resource/lung_icon.png")))

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
        self.openAction.setIcon(QIcon(resource_path("resource/open-icon.png")))

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
        """
        This class is the main widget containing displaying the lung scan.
        It opens the DICOM files and apply the b line detection algorithm.
        :param parent:
        """
        super(MainGui, self).__init__(parent)

        # grid layout
        self.hlayout_main = QHBoxLayout(self)
        self.setLayout(self.hlayout_main)

        # button
        self.prevButton = QPushButton("Prev")
        self.prevButton.setDisabled(True)
        self.nextButton = QPushButton("Next")
        self.nextButton.setDisabled(True)
        self.selectBlineAreaButton = QPushButton("Select Bline area ...")
        self.selectBlineAreaButton.setDisabled(True)

        # qcheckbox
        self.qcheckbox_show_filter = QCheckBox("Show B line(s)")
        self.qcheckbox_show_filter.setDisabled(True)

        # qgoup box
        self.qgroup_info = QGroupBox("Informations")

        # qlabel
        self.label_image = QLabelSelectable.QLabelSelectable(self)
        self.label_image.setPixmap(QPixmap('Resource/no-image-icon.png').scaled(800, 600))
        self.label_image.setFixedSize(800, 600)

        self.label_index_image = QLabel(self)

        self.label_nb_line_detected = QLabel("Number of line detected : ")
        self.label_average_line_detected = QLabel("Average line detected : ")
        self.label_percentage_black_white = QLabel("Ratio of black/white : ")
        self.label_filepath = QLabel("Filepath : ")

        # qtree widget
        self.model = QFileSystemModel()
        self.model.setRootPath(os.path.normpath(Path.home()))
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        # signal
        self.filePath.connect(self.readDicomFile)
        self.fileArray.connect(self.display_image)
        self.prevButton.clicked.connect(self.prev_image)
        self.nextButton.clicked.connect(self.next_image)
        self.selectBlineAreaButton.clicked.connect(self.startSelection)
        self.qcheckbox_show_filter.stateChanged.connect(self.startFiltering)
        self.tree.doubleClicked.connect(self.tree_open_file)
        self.label_image.selectionFinished.connect(self.selectionDone)
        self.label_image.selectionFinished.connect(self.ComputeBlackWhitePixelRatio)

        # horizontal layout for loading info and go back button
        self.hlayout_change_buttons = QHBoxLayout()
        self.hlayout_change_buttons.addStretch(0)
        self.hlayout_change_buttons.addWidget(self.prevButton)
        self.hlayout_change_buttons.addWidget(self.label_index_image)
        self.hlayout_change_buttons.addWidget(self.nextButton)
        self.hlayout_change_buttons.addStretch(0)

        # vlayout
        self.vlayout_checkbox = QVBoxLayout()
        self.vlayout_checkbox.addWidget(self.selectBlineAreaButton)
        self.vlayout_checkbox.addWidget(self.qcheckbox_show_filter)

        self.vlayout_info_label = QVBoxLayout()
        self.vlayout_info_label.addWidget(self.label_nb_line_detected)
        self.vlayout_info_label.addWidget(self.label_average_line_detected)
        self.vlayout_info_label.addWidget(self.label_percentage_black_white)
        self.vlayout_info_label.addWidget(self.label_filepath)
        self.vlayout_info_label.addStretch(0)
        self.qgroup_info.setLayout(self.vlayout_info_label)

        self.vlayout_checkbox.addWidget(self.qgroup_info)
        self.vlayout_checkbox.addStretch(0)

        # hlayout
        self.hlayout_display = QVBoxLayout()
        self.hlayout_display.addWidget(self.label_image)
        self.hlayout_display.addStretch(0)
        self.hlayout_display.addLayout(self.hlayout_change_buttons)

        # gui layout
        self.hlayout_main.addWidget(self.tree)
        self.hlayout_main.addStretch(0)
        self.hlayout_main.addLayout(self.hlayout_display)
        self.hlayout_main.addStretch(0)
        self.hlayout_main.addLayout(self.vlayout_checkbox)

        # model
        self.dicomFilePath = None
        self.imageArray = None
        self.image_index = 0
        self.selectedPixmap = None

    @pyqtSlot(QModelIndex)
    def tree_open_file(self, index):
        self.dicomFilePath = self.model.filePath(index)
        self.filePath.emit(str(self.dicomFilePath))


    def ComputeBlackWhitePixelRatio(self):
        ratio = ComputeBlackWhitePercent(self.selectedPixmap)

        ratio.getRatio()
        self.label_percentage_black_white.setText("Ratio of black/white : " + "{0:0.1f}".format(ratio.getRatio()) + " %")

    def selectionDone(self):
        self.qcheckbox_show_filter.setDisabled(False)

        image = self.imageArray[self.image_index]

        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_Indexed8)
        pix = QPixmap(image)

        self.selectedPixmap = pix.copy(self.label_image.rubberBand.geometry())

    def startSelection(self):

        image = self.imageArray[self.image_index]

        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_Indexed8)
        pix = QPixmap(image)

        self.label_image.setPixmap(pix)

        self.label_image.reset()

        self.label_image.startSelection = True

    def startFiltering(self):
        """
        This function is used to call filtering function when the bline area has been selected.
        The variable to use is self.selectedPixmap
        """
        if self.qcheckbox_show_filter.isChecked():
            # start bline detection and show bline
            run = RunAlgorithms()
            result = run.runBlineDetection(self.selectedPixmap)
        else:
            # restore bline
            image = self.imageArray[self.image_index]

            image = QImage(image, image.shape[1], image.shape[0], QImage.Format_Indexed8)
            pix = QPixmap(image)

            self.label_image.setPixmap(pix)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(None, "Open DICOM File",
                                                  directory=os.path.normpath(Path.home()), filter="*")
        if fileName:
            self.dicomFilePath = fileName
            self.filePath.emit(str(self.dicomFilePath))

    @pyqtSlot(str)
    def readDicomFile(self, dicom_filepath):

        try:
            self.image_index = 0
            self.label_filepath.setText("Filepath : " + dicom_filepath)
            self.selectBlineAreaButton.setDisabled(False)


            reader = DICOMReader.DICOMReader(dicom_filepath, False)

            self.imageArray = reader.get_images_array()
            self.prevButton.setDisabled(False)
            self.nextButton.setDisabled(False)
            self.fileArray.emit()
        except Exception as e:
            print(e)
            self.errorDialog("DICOM File error", "The file you tried to open is not a DICOM file !")

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
            self.image_index -= 1
            self.label_index_image.setText(str(self.image_index) + "/" + str(self.imageArray.shape[0]))
            self.display_image(self.image_index)

    @pyqtSlot()
    def next_image(self):
        if self.image_index < self.imageArray.shape[0]:
            self.image_index += 1
            self.label_index_image.setText(str(self.image_index) + " / " + str(self.imageArray.shape[0]))
            self.display_image(self.image_index)

    def black_white_percent(self):
        pass

    def closeEvent(self, event):
        print("close event")
        print("closed")

    def errorMSG(self):
        self.errorDialog("Error !", "Error")

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
        msg.setText("Lung BLine detection is created by : \n Nathanael Ponceau")
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
