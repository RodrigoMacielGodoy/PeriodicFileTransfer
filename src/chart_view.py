from this import d
from typing import Any
from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect, QSizePolicy
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QRect, QPoint, QPointF, QTimer, QPropertyAnimation, Qt
from PyQt5.QtChart import QChartView, QPieSlice, QChart, QLineSeries, QBarSet

class ChartView(QChartView):
    def __init__(self, chart: QChart, series: Any):
        super().__init__(chart)
        self.setMouseTracking(True)
        self.cur_mouse_pos = QPoint(0,0)
        self.series = series
        self.series.hovered.connect(self.__series_hovered)
        self.__label = QLabel()
        self.__label.setParent(self)
        self.__label.hide()
        self.__label.setAlignment(Qt.AlignCenter)
        self.__label.setStyleSheet("""
            QLabel{
                color:white;
                background-color:black;
            }
        """)
        self.__opacity_effect = QGraphicsOpacityEffect(self.__label)
        self.__label.setGraphicsEffect(self.__opacity_effect)
        self.__hide_timer = QTimer()
        self.__hide_timer.setSingleShot(True)
        self.__fade_anim = QPropertyAnimation(self.__opacity_effect, b"opacity")
        self.__fade_anim.setStartValue(1.0)
        self.__fade_anim.setEndValue(0.2)
        self.__fade_anim.setDuration(800)
        self.__fade_anim.finished.connect(self.faded)
        self.__hide_timer.timeout.connect(self.__fade_anim.start)
        self.__show_label = False
        self.__label_offset = QPoint(10,10)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.cur_mouse_pos = event.pos()
        if self.__show_label:
            bot_right = self.cur_mouse_pos + QPoint(50,20)
            top_left = self.cur_mouse_pos + self.__label_offset
            self.__label.move(top_left)
        return super().mouseMoveEvent(event)

    def faded(self) -> None:
        self.__label.hide()
        self.__show_label = False

    def __series_hovered(self, *args: Any) -> None:
        if len(args) == 2:
            obj = args[0]
            state = args[1]
        elif len(args) == 3:
            obj = args[2]
            state = args[0]
            index = args[1]
        else:
            return

        self.__show_label = state
        if state is False:
            return
        
        if type(obj) is QPieSlice:
            self.__label.setText(f"{obj.percentage()*100.0:0.2f} %")
        elif type(obj) is QLineSeries:
            pass
        elif type(obj) is QBarSet:
            self.__label.setText(f"{obj.at(index):0.0f} bytes")
            self
        else:
            self.__show_label = False
            return
        self.__label.adjustSize()
        self.__label.updateGeometry()
        if self.__hide_timer.isActive():
            self.__hide_timer.stop()
        self.__fade_anim.stop()
        self.__opacity_effect.setOpacity(1.0)
        self.__label.show()
        self.__hide_timer.start(3000)