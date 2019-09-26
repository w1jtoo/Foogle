import threading

class Terminal(object): 

    def __init__(self, *args, **kwargs):
        self.objects = []

    def initialize_thread(self):
        t = threading.Thread(target=self.loop)
        t.start()

    def loop(self):
        pass