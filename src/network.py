class Network:
    def __init__(self, maxDelay):
        self.messages = {}
        self.maxDelay = maxDelay

    def send(self, msg, to):
        if to not in self.messages:
            self.messages[to] = [msg]
        else:
            self.messages[to].append(msg)

    def receive(self, fromm):
        if fromm in self.messages:
            if len(self.messages[fromm]) > 0:
                return self.messages[fromm].pop(0)
        return None

    def getMaxDelay(self):
        return self.maxDelay
