# This class enables logging actions to the console
class Logger:
    def __init__(self, log_=True):
        self.log = log_

    def Log(self, text):
        if self.log:
            print(text)
