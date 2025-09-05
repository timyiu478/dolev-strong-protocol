from datetime import datetime


class Clock:
    def __init__(self, roundTW, f):
        self.roundTW = roundTW
        self.f = f
        self.startTime = datetime.now()

    # get current time in terms of round
    # clock cycle from 0 to f + 1
    def now(self):
        return ((datetime.now() - self.startTime) // self.roundTW) % (self.f + 2)
