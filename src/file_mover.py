import os
import re
import shutil
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from mover import Mover


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
        self.__movers: list[Mover] = []

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

    def close(self) -> None:
        for mover in self.__movers:
            mover.wait()

    def __check_files(self) -> None:
        # TODO: add recursive files if settings available 
        # (create the same tree or copy to root dst?)
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
        if self.__source == "" or self.__destination == "":
            return

        if (not os.path.exists(self.__source) or
                not os.path.exists(self.__destination)):
            return
        
        src = os.path.join(self.__source, file)
        dst = os.path.join(self.__destination, file)
        
        # TODO: maybe create a move method to move large files in batches 
        # so it can be stopped, preventing application hangging on close,
        # giving the option to cancel the move cmd and preventing corruption
        # of files if application is forced to close.

        self.__movers.append(Mover(src, dst, self.__emit_finished_transfer,
                            (self.__source, self.__destination, file)))
        self.__movers[-1].start()

    def __emit_finished_transfer(self, src: str, dst: str, file: str) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fileTransfered.emit(self.__source, self.__destination, file, now)