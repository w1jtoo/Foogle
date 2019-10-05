import abc


class TerminalObj(object, metaclass=abc.ABCMeta):
    def __init__(self, startX: int, startY: int, endX: int, endY: int):
        pass

    @property
    def side(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def update(self):
        """ Should return position chosen by this AI  
        """
        raise NotImplementedError
