from datetime import datetime


class Clock:
    def __init__(self, roundTW, f):
        self.roundTW = roundTW
        self.f = f
        self.startTime = datetime.now()

    # get current time in terms of round
    # clock cycle from 0 to f + 2
    # f + 2 round for deciding values
    def now(self):
        return ((datetime.now() - self.startTime) // self.roundTW) % (self.f + 3)

    def cycle(self):
        return (datetime.now() - self.startTime) // self.roundTW // (self.f + 3)
