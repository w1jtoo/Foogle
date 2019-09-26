from App.AppContainer import AppContainer
from App.Terminal.Teminal import Terminal

class Application():
    def __init__(self):
        self.container = AppContainer()

        self.terminal = Terminal(self.container)
        

    def init_container(self):
        pass

    def run(self):
        raise NotImplementedError
