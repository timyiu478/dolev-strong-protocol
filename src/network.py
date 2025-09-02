class Socket:
    def __init__(self, network, src):
        self.network = network
        self.src = src

    def send(self, msg, dst):
        self.network.send(msg, dst)

    def receive(self):
        return self.network.receive(self.src)


class Network:
    def __init__(self, maxDelay):
        self.messages = {}
        self.maxDelay = maxDelay

    def send(self, msg, dst):
        if dst not in self.messages:
            self.messages[dst] = [msg]
        else:
            self.messages[dst].append(msg)

    def receive(self, addr):
        if addr in self.messages:
            if len(self.messages[addr]) > 0:
                return self.messages[addr].pop(0)
        return None

    def maxDelay(self):
        return self.maxDelay
