import os
import re
import shutil
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class FileMover(QObject):
    fileTransfered = pyqtSignal(str, str, str, str)
    def __init__(self) -> None:
        super().__init__()
        self.__file_check_timer = QTimer()
        self.__file_check_timer.timeout.connect(self.__check_files)
        self.__regex = ""
        self.__source = ""
        self.__destination = ""
        self.__period = 0

    @property
    def source(self) -> str:
        return self.__source

    @property
    def destination(self) -> str:
        return self.__destination

    @property
    def regex(self) -> str:
        return self.__regex

    @property
    def period(self) -> int:
        return self.__period

    @property
    def isRunning(self) -> bool:
        return self.__file_check_timer.isActive()

    def setPeriod(self, period: int) -> None:
        self.__period = period*1000

    def setDestination(self, dest: str) -> None:
        self.__destination = dest
    
    def setSource(self, src: str) -> None:
        self.__source = src

    def setRegex(self, regex: str) -> None:
        self.__regex = regex

    def start(self) -> bool:
        if self.__period <= 0:
            return False
        self.__check_files()
        self.__file_check_timer.start(self.__period)
        return True

    def stop(self) -> None:
        if self.__file_check_timer.isActive():
            self.__file_check_timer.stop()

    def __check_files(self) -> None:
        files = os.listdir(self.__source)
        for file in files:
            path = os.path.join(self.__source, file)
            if not os.path.isfile(path):
                continue
            match = len(re.findall(self.__regex, file)) > 0
            if not match:
                continue

            self.__move(file)

    def __move(self, file: str) -> None:
        # TODO: make the move async, just in case the files are too
        # large (or too many), to prevent the GUI to freeze
        if self.__source == "" or self.__destination == "":
            return

        if (not os.path.exists(self.__source) or
                not os.path.exists(self.__destination)):
            return
        
        src = os.path.join(self.__source, file)
        dst = os.path.join(self.__destination, file)

        shutil.move(src, dst)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fileTransfered.emit(self.__source, self.__destination, file, now)
