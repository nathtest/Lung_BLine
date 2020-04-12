import random, sys
from PyQt5.QtCore import QPoint, QRect, QSize, Qt,pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QLabel, QApplication, QRubberBand


class QLabelSelectable(QLabel):
    selectionFinished = pyqtSignal()

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        self.startSelection = False
        self.endSelection = False


    def reset(self):
        self.startSelection = False
        self.endSelection = False


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.startSelection and not self.endSelection:
            self.origin = QPoint(event.pos())
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull() and self.startSelection and not self.endSelection:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.startSelection:
            #print(self.rubberBand.geometry())

            self.drawRectangle()

            self.rubberBand.hide()

            self.endSelection = True

    def drawRectangle(self):
        # create painter instance with pixmap
        self.painterInstance = QPainter(self.pixmap())

        # set rectangle color and thickness
        self.penRectangle = QPen(Qt.red)
        self.penRectangle.setWidth(3)

        # draw rectangle on painter
        self.painterInstance.setPen(self.penRectangle)
        self.painterInstance.drawRect(self.rubberBand.geometry())
        self.selectionFinished.emit()

def create_pixmap():
    def color():
        r = random.randrange(0, 255)
        g = random.randrange(0, 255)
        b = random.randrange(0, 255)
        return QColor(r, g, b)

    def point():
        return QPoint(random.randrange(0, 400), random.randrange(0, 300))

    pixmap = QPixmap(400, 300)
    pixmap.fill(color())
    painter = QPainter()
    painter.begin(pixmap)
    i = 0
    while i < 1000:
        painter.setBrush(color())
        painter.drawPolygon(QPolygon([point(), point(), point()]))
        i += 1

    painter.end()
    return pixmap


if __name__ == "__main__":
    app = QApplication(sys.argv)
    random.seed()

    window = QLabelSelectable()
    window.setPixmap(create_pixmap())
    window.resize(400, 300)
    window.show()

    sys.exit(app.exec_())
