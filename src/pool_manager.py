from PyQt5.sip import wrappertype
from PyQt5.QtCore import QObject, pyqtSignal


class Protected(wrappertype):
    __SENTINEL = object()
    def __new__(mcs, name, bases, class_dict):
        private = {key for base in bases for key, value in vars(
            base).items() if callable(value) and mcs.__is_final(value)}
        if any(key in private for key in class_dict):
            raise RuntimeError("Certain methods may not be overriden")
        return super().__new__(mcs, name, bases, class_dict)

    @classmethod
    def __is_final(mcs, method):
        try:
            return method.__final is mcs.__SENTINEL
        except AttributeError:
            return False

    @classmethod
    def final(mcs, method):
        method.__final = mcs.__SENTINEL
        return method

class PoolManager(object):
    """
        A class to manage instantiation of PoolObjects and keep objects reusabily.
    """

    class PoolObject(QObject, metaclass=Protected):
        """
            A reusable object to be used with the PoolManager. The `release` method
            and the `releases` signal must not be overriden!
        """
        released = pyqtSignal(QObject)

        @Protected.final
        def release(self) -> None:
            self.released.emit(self)

    def __init__(self, object_class: PoolObject,
                 initial_size: int=10,
                 max_size: int=-1) -> None:
        
        if not issubclass(object_class, PoolManager.PoolObject):
            raise ValueError("object_class must be of type PoolObject"
                              f" and not {type(object_class)}")

        self.__max_size = max_size
        self.__object_class = object_class
        self.__idle_objects: list[PoolManager.PoolObject] = []
        self.__using_objects: list[PoolManager.PoolObject] = []

        for _ in range(initial_size):
            self.__idle_objects.append(self.__new_object())

    @property
    def objects_in_use(self) -> int:
        return len(self.__using_objects)

    @property
    def objects_in_idle(self) -> int:
        return len(self.__idle_objects)

    def __new_object(self) -> PoolObject:
        obj = self.__object_class()
        obj.released.connect(self.__object_released)
        return obj

    def __object_released(self, obj: PoolObject) -> None:
        self.__using_objects.remove(obj)
        self.__idle_objects.append(obj)

    def get_object(self) -> PoolObject:
        if len(self.__idle_objects) == 0:
            if self.__max_size > 0:
                raise IndexError("You are trying to get more"
                                " objects in memory than the"
                                " maximum specified.")
            else:
                self.__idle_objects.append(self.__new_object())

        obj = self.__idle_objects.pop(0)
        self.__using_objects.append(obj)
        return obj
