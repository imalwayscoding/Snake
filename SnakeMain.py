from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from Game import *
import sys


class Form(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(700, 700)
        self.game = Game(self)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)

        self.game.draw(qp)

        qp.end()

    def keyPressEvent(self, e):
        self.game.keyPressed(e.key())

    def closeEvent(self, e):
        self.game.bRun = False

    def onGameOver(self):
        result = QMessageBox.information(self, 'Game Over', 'Retry (Yes), Exit (No)', QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            del self.game
            self.game = Game(self)
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())
