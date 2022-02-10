import shutil
from typing import Callable
from PyQt5.QtCore import QThread, pyqtSignal

from pool_manager import PoolManager

class Mover(PoolManager.PoolObject):
    __moveFinished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.__thread = QThread(self)
        self.__thread.run = self.run

    def initialize(self, src: str, dst: str, callback: Callable=None,
                args: tuple=(), kwargs: dict={},
                move_func: Callable=shutil.move) -> None:
        self.__source = src
        self.__destination = dst
        self.__callback = callback
        self.__callback_args = args
        self.__callback_kwargs = kwargs
        self.__move_func = move_func
        self.__moveFinished.connect(self.__finished)

    def __finished(self) -> None:
        if self.__callback is None:
            return
        self.__callback(*self.__callback_args, **self.__callback_kwargs)
        self.release()

    def start(self):
        self.__thread.start()

    def wait(self):
        self.__thread.wait()

    def run(self) -> None:
        self.__move_func(self.__source, self.__destination)
        self.__moveFinished.emit()
