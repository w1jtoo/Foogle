import threading


class Terminal(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def sprint(self, string: str) -> None:
        print(string)

    def loop(self):
        pass
