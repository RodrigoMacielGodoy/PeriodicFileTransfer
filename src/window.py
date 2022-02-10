import os

from numpy import dtype
from PyQt5.QtChart import (QBarCategoryAxis, QBarSeries, QBarSet, QChart,
                           QLineSeries, QPieSeries, QPieSlice, QChartView,
                           QAbstractBarSeries, QStackedBarSeries)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QIntValidator, QPainter
from PyQt5.QtWidgets import QFileDialog, QLabel, QMainWindow, QTableWidgetItem

from chart_view import ChartView
from file_mover import FileMover
from logger import Logger
from main_window_layout import Ui_MainWindow
from settings import HOME_PATH, LOCAL_PATH, Settings


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.time_units_mult = {
            0: 1,
            1: 60,
            2: 3600
        }
        
        self.file_logger = Logger(os.path.join(LOCAL_PATH, "file_move_log.csv"))

        self.settings = Settings(os.path.join(LOCAL_PATH, "config.json"))
        default_settings = {
            "source": "",
            "destination": "",
            "regex": "",
            "period": 10,
            "period_unit": 0,
            "recursive_matches": False
        }
        self.settings.load()
        has_all = True
        for key, value in default_settings.items():
            if self.settings.has(key):
                continue
            self.settings.setField(key, value)
            has_all = False
        if not has_all:
            self.settings.save()

        self.file_mover = FileMover()
        self.update_file_mover()
        self.ui = Ui_MainWindow()
        self.setupUI()

    def __get_directory(self) -> str:
        return QFileDialog.getExistingDirectory(self, HOME_PATH)

    def closeEvent(self, evt) -> None:
        self.file_mover.stop()
        self.file_mover.close()
        evt.accept()

    def setupUI(self) -> None:
        self.ui.setupUi(self)
        self.ui.le_period.setValidator(QIntValidator(self.ui.le_period))
        self.lb_chart_hover = QLabel()

        self.line_chart = QChart()

        self.pie_chart = QChart()
        layout = self.pie_chart.layout()
        layout.setContentsMargins(0,0,0,0)
        self.pie_series = QPieSeries(self.pie_chart)
        self.pie_series.setPieSize(1)
        legend = self.pie_chart.legend()
        legend.setLabelColor(QColor(230,230,230))
        legend.setAlignment(Qt.AlignRight)
        self.pie_chart.setTitle("Quantity of Transfers per Extension")
        self.pie_chart.setTitleBrush(QBrush(QColor(255,255,255)))
        self.pie_chart.addSeries(self.pie_series)
        self.pie_chart.setBackgroundVisible(False)
        self.pie_chart_view = ChartView(self.pie_chart, self.pie_series)
        self.pie_chart_view.setRenderHint(QPainter.Antialiasing)
        self.pie_chart_view.setStyleSheet("""
                background-color:transparent;
        """)

        self.bar_chart = QChart()
        layout = self.bar_chart.layout()
        layout.setContentsMargins(0,0,0,0)

        self.bar_chart.setBackgroundVisible(False)
        self.bar_series = QBarSeries()
        legend = self.bar_chart.legend()
        legend.setLabelColor(QColor(230,230,230))
        legend.setAlignment(Qt.AlignBottom)
        self.bar_chart.setTitle("Average File Size per Extension Transfered")
        self.bar_chart.setTitleBrush(QBrush(QColor(255,255,255)))
        self.bar_chart_view = ChartView(self.bar_chart, self.bar_series)
        self.bar_chart_view.setRenderHint(QPainter.Antialiasing)
        self.bar_chart_view.setStyleSheet("""
                background-color:transparent;
        """)

        self.line_chart = QChart()
        layout = self.line_chart.layout()
        layout.setContentsMargins(0,0,0,0)
        self.line_series = QLineSeries(self.line_chart)
        self.line_chart.setBackgroundVisible(False)
        legend = self.line_chart.legend()
        legend.setLabelColor(QColor(230,230,230))
        legend.setAlignment(Qt.AlignBottom)
        self.line_chart.setTitle("Files Transfered per Date")
        self.line_chart.setTitleBrush(QBrush(QColor(255,255,255)))
        self.line_chart_view = ChartView(self.line_chart, self.line_series)
        self.line_chart_view.setRenderHint(QPainter.Antialiasing)
        self.line_chart_view.setStyleSheet("""
                background-color:transparent;
        """)
        
        
        layout = self.ui.charts_tab.layout()
        layout.addWidget(self.pie_chart_view, 0, 0, 1, 1)
        layout.addWidget(self.line_chart_view, 0, 1, 1, 1)
        layout.addWidget(self.bar_chart_view, 2, 0, 1, 2)


        self.updateUi()
        self.update_log_table()
        self.update_charts()
        self.setupConnects()

    def setupConnects(self) -> None:
        self.file_mover.fileTransfered.connect(self.file_logger.log_file_tranfered)
        self.file_logger.logChanged.connect(self.log_changed)

        self.ui.bt_start_stop.clicked.connect(self.start_stop_clicked)

        self.ui.le_file_regex.textChanged.connect(self.regex_changed)
        self.ui.le_period.textChanged.connect(self.period_changed)
        self.ui.bt_set_src_dir.clicked.connect(self.source_dir_changed)
        self.ui.bt_set_dest_dir.clicked.connect(self.destination_dir_changed)
        self.ui.cb_period_unit.currentIndexChanged.connect(self.period_unit_changed)

        self.ui.bt_swap_src_dst.clicked.connect(self.swap_src_dst)

    def set_config_enabled(self, enabled: bool) -> None:
        self.ui.le_file_regex.setEnabled(enabled)
        self.ui.le_period.setEnabled(enabled)
        self.ui.bt_set_src_dir.setEnabled(enabled)
        self.ui.bt_set_dest_dir.setEnabled(enabled)
        self.ui.cb_period_unit.setEnabled(enabled)
        self.ui.bt_swap_src_dst.setEnabled(enabled)
        self.ui.lb_destination_dir.setEnabled(enabled)
        self.ui.lb_source_dir.setEnabled(enabled)
        self.ui.lb_file_regex.setEnabled(enabled)
        self.ui.lb_period.setEnabled(enabled)

    def update_file_mover(self) -> None:
        self.file_mover.setDestination(self.settings.destination)
        self.file_mover.setSource(self.settings.source)
        mult = self.time_units_mult[self.settings.period_unit]
        self.file_mover.setPeriod(self.settings.period * mult)
        self.file_mover.setRegex(self.settings.regex)

    def updateUi(self) -> None:
        self.ui.le_file_regex.setText(self.settings.regex)
        self.ui.le_period.setText(str(self.settings.period))
        self.ui.lb_destination_dir.setText(self.settings.destination or "Select a directory")
        self.ui.lb_source_dir.setText(self.settings.source or "Select a directory")
        self.ui.cb_period_unit.setCurrentIndex(self.settings.period_unit)

    def log_changed(self) -> None:
        self.update_log_table()
        self.update_charts()

    def update_log_table(self) -> None:
        log_data = self.file_logger.get_log()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setRowCount(len(log_data))
        for row, row_data in enumerate(log_data):
            for col, col_data in enumerate(row_data):
                self.ui.tableWidget.setItem(row, col, QTableWidgetItem(col_data))

    def update_charts(self) -> None:
        log_data = self.file_logger.get_log()

        # Pie Chart - Quantity of files with same extension
        extensions = [row[3] for row in log_data]
        pie_data = {}

        for ext in extensions:
            if ext not in pie_data:
                pie_data[ext] = 0
            pie_data[ext] += 1

        self.pie_series.clear()

        for extension, quantity in pie_data.items():
            self.pie_series.append(extension, quantity)
        
        for slice_ in self.pie_series.slices():
            slice_.setLabelColor(QColor(255,255,255))

        self.pie_series.setLabelsVisible(True)
        self.pie_series.setLabelsPosition(QPieSlice.LabelInsideNormal)

        # Bar Chart - Average file size per extension
        extension_sizes = [(row[3], row[6]) for row in log_data]
        ext_total_size = {}
        ext_count = {}
        for pt in extension_sizes:
            ext = pt[0]
            size = int(pt[1])
            if ext not in ext_total_size:
                ext_total_size[ext] = 0
                ext_count[ext] = 0
            ext_total_size[ext] += size
            ext_count[ext] += 1

        data = sorted(ext_total_size.items(), key=lambda x: x[1]/ext_count[x[0]], reverse=True)

        self.bar_chart.removeAllSeries()
        self.bar_series.clear()
        for key,value in data:
            bar_set = QBarSet(key)
            bar_set.append(value/ext_count[key])
            bar_set.setLabelColor(QColor(230,230,230))
            self.bar_series.append(bar_set)
        if self.bar_series not in self.bar_chart.series():
            self.bar_chart.addSeries(self.bar_series)

        # Line Chart - Files moved per day

        date_data = {}
        for date in [row[0] for row in log_data]:
            if date not in date_data:
                date_data[date] = 0
            date_data[date] += 1
        
        sorted_date_data = sorted(date_data.items(), key=lambda x: x[1], reverse=True)
        
        self.line_series.clear()
        for i,pt in enumerate(sorted_date_data):
            self.line_series.append(i, pt[1])
        
        if self.line_series not in self.line_chart.series():
            self.line_chart.addSeries(self.line_series)
            self.line_chart.createDefaultAxes()
            axes = self.line_chart.axes()
            for axis in axes:
                axis.setLabelsColor(QColor(230,230,230))

    def swap_src_dst(self) -> None:
        dst, src = self.settings.source, self.settings.destination
        self.settings.setField("destination", dst)
        self.settings.setField("source", src)
        self.settings.save()
        self.update_file_mover()
        self.updateUi()

    def source_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.settings.setField("source", path)
        self.settings.save()
        self.update_file_mover()
        self.updateUi()
    
    def destination_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.settings.setField("destination", path)
        self.settings.save()
        self.update_file_mover()
        self.updateUi()

    def start_stop_clicked(self) -> None:
        running_state = self.file_mover.isRunning

        if running_state is True:
            self.file_mover.stop()
        else:
            self.file_mover.start()

        running_state = self.file_mover.isRunning
        self.set_config_enabled(not running_state)
        txt = "Stop" if running_state else "Start"

        self.ui.bt_start_stop.setText(txt)

    def regex_changed(self, txt: str) -> None:
        self.settings.setField("regex", txt)
        self.settings.save()
        self.update_file_mover()

    def period_changed(self, txt: str) -> None:
        try:
            period = int(txt)
        except ValueError:
            return
        self.settings.setField("period", period)
        self.update_file_mover()

    def period_unit_changed(self, index: int) -> None:
        if index > 2 or index < 0:
            return

        self.settings.setField("period_unit", index)
        self.settings.save()
        self.update_file_mover()
