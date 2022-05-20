class DiputadeNotFound(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MultiplesDiputadesFound(Exception):
    def __init__(self, message,names):
        self.message = message
        self.names = names
        super().__init__(self.message)
