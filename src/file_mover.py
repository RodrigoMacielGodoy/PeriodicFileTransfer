from multiprocessing import Pool
import os
import re
import shutil
from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

from mover import Mover
from pool_manager import PoolManager


class FileMover(QObject):
    fileTransfered = pyqtSignal(dict)
    def __init__(self) -> None:
        super().__init__()
        self.__file_check_timer = QTimer()
        self.__file_check_timer.timeout.connect(self.__check_files)
        self.__regex = ""
        self.__source = ""
        self.__destination = ""
        self.__period = 0
        self.__movers = PoolManager(Mover)

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
        while(self.__movers.objects_in_use > 0):
            pass

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
        data = {
            "Source":self.__source,
            "Destination":self.__destination,
            "file":file,
            "Size [bytes]":os.stat(src).st_size,
            "start_time": datetime.now()
        }
        mover =self.__movers.get_object()
        mover.initialize(src, dst, self.__emit_finished_transfer, args=(data,))
        mover.start()

    def __emit_finished_transfer(self, data: dict) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now_date, now_hour = now.split(" ")
        transfer_time = (datetime.now() - data["start_time"]).microseconds
        file_name, ext = os.path.splitext(data["file"])
        new_data = {
            "Date": now_date,
            "Hour": now_hour,
            "File Name": file_name,
            "Extension": ext,
            "Transfer Time [us]": transfer_time
        }
        data.pop("start_time")
        data.pop("file")
        data.update(new_data)
        
        self.fileTransfered.emit(data)
