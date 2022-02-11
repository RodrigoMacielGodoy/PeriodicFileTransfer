from typing import Any

from PyQt5.QtChart import QBarSet, QChart, QChartView, QLineSeries, QPieSlice
from PyQt5.QtCore import QPoint, QPointF, QPropertyAnimation, QRect, Qt, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel


class ChartView(QChartView):
    def __init__(self, chart: QChart, series: Any=None):
        super().__init__(chart)
        self.setMouseTracking(True)
        self.__chart = chart
        self.cur_mouse_pos = QPoint(0,0)
        self.__is_line_series = False
        self.series = series
        if self.series is not None:
            self.series.hovered.connect(self.__series_hovered)
            self.__is_line_series = isinstance(series, QLineSeries)

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
        self.__last_mouse_pos = QPoint(0,0)

    def set_series(self, series: list) -> None:
        for serie in series:
            serie.hovered.connect(self.__series_hovered)

    def set_serie(self, serie) -> None:
        serie.hovered.connect(self.__series_hovered)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.cur_mouse_pos = event.pos()
        if self.__show_label or self.__is_line_series:
            top_left = self.cur_mouse_pos + self.__label_offset
            self.__label.move(top_left)
            if self.__is_line_series:
                self.__opacity_effect.setOpacity(1.0)
                if self.__label.isHidden():
                    self.__label.show()
                point = self.__chart.mapToValue(self.cur_mouse_pos)
                self.__label.setText(f"{point.y():0.2f}")
                self.__label.adjustSize()
        return super().mouseMoveEvent(event)

    def enterEvent(self, a0) -> None:
        if self.__hide_timer.isActive():
            self.__hide_timer.stop()
        self.__fade_anim.stop()
        return super().enterEvent(a0)

    def leaveEvent(self, a0) -> None:
        if self.__hide_timer.isActive():
            self.__hide_timer.stop()
        self.__fade_anim.start()
        return super().leaveEvent(a0)

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
            self.__label.setText(f"{obj.y():0.0f}")
        elif type(obj) is QBarSet:
            self.__label.setText(f"{obj.at(index):0.0f} bytes")
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
