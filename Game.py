import random

from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtCore import Qt, QSizeF, QRectF, QPoint, QObject, pyqtSignal
from threading import Thread
import time


class Game(QObject):
    signal_update = pyqtSignal()
    signal_GameOver = pyqtSignal()

    def __init__(self, w):

        super().__init__()

        self.parent = w
        self.rect = w.rect()
        self.inrect = QRectF(self.rect)

        gap = 20
        self.inrect.adjust(gap, gap, -gap, -gap)

        # 게임판 라인수, 게임판 한칸 크기
        self.line = 20
        self.size = self.inrect.width() / (self.line - 1)

        self.rects = []
        gap = 5
        x = self.inrect.left()
        y = self.inrect.top()
        for i in range(self.line):
            temp = []
            for j in range(self.line):
                rect = QRectF(x + (j * self.size), y + (i * self.size), self.size, self.size)
                rect.adjust(gap, gap, -gap, -gap)
                temp.append(rect)
            self.rects.append(temp)

        # 초기뱀 생성
        head = QPoint(self.line // 2, self.line // 2)
        self.snake = []
        self.snake.append(head)
        self.snake.append(QPoint(head.x() - 1, head.y()))
        self.snake.append(QPoint(head.x() - 2, head.y()))

        # 뱀방향 
        self.dir = 'Right'

        self.bFood = False
        self.fx = 0
        self.fy = 0

        self.bMoved = False

        self.signal_update.connect(self.parent.update)
        self.signal_GameOver.connect(self.parent.onGameOver)

        # th레드 생성
        self.t = Thread(target=self.threadFunc)
        self.bRun = True
        self.t.start()

    def draw(self, qp):
        # 게임판 그리기
        x = self.inrect.left()
        y = self.inrect.top()

        x1 = self.inrect.right()
        y1 = self.inrect.top()

        x2 = self.inrect.left()
        y2 = self.inrect.bottom()

        # qp.drawLine(x, y, x1, y1)

        for i in range(self.line):
            qp.drawLine(x, y + (i * self.size), x1, y1 + (i * self.size))
            qp.drawLine(x + (i * self.size), y, x2 + (i * self.size), y2)

        # 뱀 그리기            
        hb = QBrush(QColor(0, 255, 0))
        bb = QBrush(QColor(0, 255, 0, 64))

        for k, v in enumerate(self.snake):
            if k == 0:
                qp.setBrush(hb)
            else:
                qp.setBrush(bb)
            qp.drawRect(self.rects[v.y()][v.x()])

            if k == 0:
                qp.drawText(self.rects[v.y()][v.x()], Qt.AlignCenter, str(len(self.snake)-3))

        if self.bFood:
            b = QBrush(QColor(255, 255, 0))
            qp.setBrush(b)
            qp.drawEllipse(self.rects[self.fy][self.fx])

    def keyPressed(self, key):
        if not self.bMoved:
            if key == Qt.Key_Left and not self.dir == 'Right':
                self.dir = 'Left'
            if key == Qt.Key_Right and not self.dir == 'Left':
                self.dir = 'Right'
            if key == Qt.Key_Up and not self.dir == 'Down':
                self.dir = 'Up'
            if key == Qt.Key_Down and not self.dir == 'Up':
                self.dir = 'Down'
            self.bMoved = True

    def makeFood(self):

        while True:
            x = random.randint(0, self.line - 2)
            y = random.randint(0, self.line - 2)

            # 뱀 마디와 좌표 비교
            bOverlap = False
            for m in self.snake:
                if m.x() == x and m.y() == y:
                    bOverlap = True
                    break

            if not bOverlap:
                self.fx = x
                self.fy = y
                self.bFood = True
                break
            else:
                continue

    def isAte(self, hx, hy):
        if hx == self.fx and hy == self.fy:
            return True
        else:
            return False

    def isCrash(self, hx, hy):
        minimum = 4
        if len(self.snake) > minimum:
            for i, m in enumerate(self.snake):
                if i > minimum-1:
                    if hx == m.x() and hy == m.y():
                        return True
        return False

    def threadFunc(self):
        while self.bRun:

            if not self.bFood:
                self.makeFood()

            head = QPoint(self.snake[0])

            x = head.x()
            y = head.y()

            eat = self.isAte(x, y)

            if self.dir == 'Left':
                head.setX(x - 1)
            if self.dir == 'Right':
                head.setX(x + 1)
            if self.dir == 'Up':
                head.setY(y - 1)
            if self.dir == 'Down':
                head.setY(y + 1)

            # 밖으로 나간건지
            if (head.x() < 0 or head.x() >= self.line - 1) or (head.y() < 0 or head.y() >= self.line - 1):
                break
            else:
                self.snake.insert(0, head)
                if not eat:
                    del (self.snake[-1])
                else:
                    self.bFood = False

            self.bMoved = False

            if self.isCrash(head.x(), head.y()):
                break

            self.signal_update.emit()
            time.sleep(0.17)

        self.signal_GameOver.emit()
