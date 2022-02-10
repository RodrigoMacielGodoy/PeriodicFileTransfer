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
        # TODO: Generalize the logging writting the keys as header and values as row data
        src = str(data["src"])
        dst = str(data["dst"])
        file = str(data["file"])
        end_time = str(data["end_time"])
        size = str(data["size"])
        transfer_time = str(data["transfer_time"])

        header = ""
        if not os.path.exists(self.__path):
            header = "Date, Time, File, Extension, Source, Destination, Size[bytes], Transfer Time [us]\n"

        with open(self.__path, "a+") as f:
            if header:
                f.write(header)
            date, time = end_time.split(" ")
            file_name, extension = os.path.splitext(file)
            row = ",".join([date, time, file_name, extension, src, dst, size, transfer_time])
            f.write(row+"\n")
        self.logChanged.emit()
            
    def get_log(self) -> "list[list[str]]":
        if not os.path.exists(self.__path):
            return []
        with open(self.__path, "r") as f:
            file = f.read()

        data = []
        first = True
        for line in file.split("\n"):
            if first:
                first = False # Skips the header
                continue
            line_data = line.split(",")
            if len(line_data) != 8:
                continue
            data.append(line_data)
        return data