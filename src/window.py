import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QIntValidator

from main_window_layout import Ui_MainWindow
from settings import Settings, LOCAL_PATH, HOME_PATH
from file_mover import FileMover
from logger import Logger

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

    def setupUI(self) -> None:
        self.ui.setupUi(self)

        self.ui.le_period.setValidator(QIntValidator(self.ui.le_period))

        self.ui.le_file_regex.setText(self.settings.regex)
        self.ui.le_period.setText(str(self.settings.period))
        self.ui.lb_destination_dir.setText(self.settings.destination or "Select a directory")
        self.ui.lb_source_dir.setText(self.settings.source or "Select a directory")
        self.ui.cb_period_unit.setCurrentIndex(self.settings.period_unit)

        self.setupConnects()

    def setupConnects(self) -> None:
        self.file_mover.fileTransfered.connect(self.file_logger.log_file_tranfered)

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

    def swap_src_dst(self) -> None:
        self.settings.destination, self.settings.source = self.settings.source, self.settings.destination
        self.settings.save()
        self.update_file_mover()

    def source_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.ui.lb_source_dir.setText(path)
        self.settings.setField("source", path)
        self.settings.save()
        self.update_file_mover()
    
    def destination_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.ui.lb_destination_dir.setText(path)
        self.settings.setField("destination", path)
        self.settings.save()
        self.update_file_mover()

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