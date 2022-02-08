from email import header
import os

class Logger(object):
    def __init__(self, path: str, create: bool=True) -> None:
        self.__path = path
        if not os.path.exists(os.path.dirname(self.__path)):
            os.mkdir(os.path.dirname(self.__path))

    def log_file_tranfered(self, src: str, dst: str, file: str, datetime: str) -> None:
        header = ""
        if not os.path.exists(self.__path):
            header = "Date, Time, File, Extension, Source, Destination\n\r"

        with open(self.__path, "a+") as f:
            if header:
                f.write(header)
            date, time = datetime.split(" ")
            file_name, extension = os.path.splitext(file)
            row = ",".join([date, time, file_name, extension, src, dst])
            f.write(row+"\n\r")
            