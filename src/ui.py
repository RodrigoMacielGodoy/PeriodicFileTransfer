import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QIntValidator

from main_window_layout import Ui_MainWindow
from settings import Settings, LOCAL_PATH, HOME_PATH
from file_mover import FileMover

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.time_units_mult = {
            0: 1,
            1: 60,
            2: 3600
        }

        self.settings = Settings(os.path.join(LOCAL_PATH, "config.json"))
        default_settings = {
            "source": "",
            "destination": "",
            "regex": "",
            "period": 10,
            "time_unit": 0,
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
        self.file_mover.setSource(self.settings.source)
        self.file_mover.setDestination(self.settings.destination)
        self.file_mover.setPeriod(self.settings.period)
        self.file_mover.setRegex(self.settings.regex)

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
        self.ui.cb_period_unit.setCurrentIndex(self.settings.time_unit)

        self.setupConnects()

    def setupConnects(self) -> None:
        #TODO: add behaviour for time unit combo box
        #TODO: add swap src/dst behaviour
        self.ui.bt_start_stop.clicked.connect(self.start_stop_clicked)

        self.ui.le_file_regex.textChanged.connect(self.regex_changed)
        self.ui.le_period.textChanged.connect(self.period_changed)
        self.ui.bt_set_src_dir.clicked.connect(self.source_dir_changed)
        self.ui.bt_set_dest_dir.clicked.connect(self.destination_dir_changed)

    def source_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.ui.lb_source_dir.setText(path)
        self.settings.setField("source", path)
        self.settings.save()
        self.file_mover.setSource(path)
    
    def destination_dir_changed(self) -> None:
        path = self.__get_directory()
        if path == "":
            return

        self.ui.lb_destination_dir.setText(path)
        self.settings.setField("destination", path)
        self.settings.save()
        self.file_mover.setDestination(path)

    def start_stop_clicked(self) -> None:
        #TODO: block/unblock changes in configurations based on running state
        if self.file_mover.isRunning:
            self.file_mover.stop()
        else:
            self.file_mover.start()

        txt = "Stop" if self.file_mover.isRunning else "Star"

        self.ui.bt_start_stop.setText(txt)

    def regex_changed(self, txt: str) -> None:
        self.settings.setField("regex", txt)
        self.settings.save()
        self.file_mover.setRegex(txt)

    def period_changed(self, txt: str) -> None:
        # FIXME: Multiply perid by unit choosen
        try:
            period = int(txt)
        except ValueError:
            return
        self.settings.setField("period", period)
        self.file_mover.setPeriod(period*1000)