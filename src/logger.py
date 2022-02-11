import os

from PyQt5.QtCore import QObject, pyqtSignal

class Logger(QObject):
    logChanged = pyqtSignal()
    def __init__(self, path: str, create: bool=True) -> None:
        super().__init__()
        self.__path = path
        if not os.path.exists(os.path.dirname(self.__path)):
            os.mkdir(os.path.dirname(self.__path))

    def log_file_tranfered(self, data: dict) -> None:
        header = ""
        if not os.path.exists(self.__path):
            header = ",".join(data.keys())+"\n"

        with open(self.__path, "a+") as f:
            if header:
                f.write(header)
            row = ",".join([str(val) for val in data.values()])
            f.write(row+"\n")
        self.logChanged.emit()
            
    def get_log(self) -> "list[list[str]]":
        if not os.path.exists(self.__path):
            return []
        with open(self.__path, "r") as f:
            file = f.read()

        data = []
        header = []
        first = True
        for line in file.split("\n"):
            if line == "":
                continue
            row_dict = {}
            line_data = line.split(",")
            if first:
                first = False # Skips the header
                header = line_data
                continue
            for i in range(len(line_data)):
                row_dict[header[i]] = line_data[i]
            data.append(row_dict)
        return data