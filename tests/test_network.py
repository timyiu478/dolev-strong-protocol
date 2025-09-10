import unittest
from src.network import Network


class DummyClock:
    """Manual clock for controlling rounds."""
    def __init__(self, start=0):
        self._round = start

    def now(self):
        return self._round

    def set(self, round):
        self._round = round


class TestNetworkFIFO(unittest.TestCase):
    def setUp(self):
        self.peers = ['A', 'B']
        self.f = 1
        self.clock = DummyClock()
        self.network = Network(self.clock, self.peers, self.f)
        self.socketA = self.network.createSocket('A')
        self.socketB = self.network.createSocket('B')

    def test_fifo_delivery_single_round(self):
        # Send 3 messages from A to B for next round
        messages = ['msg1', 'msg2', 'msg3']
        for msg in messages:
            self.socketA.send(msg, 'B')
        # Advance clock to next round so B can receive
        self.clock.set(1)
        received = []
        for _ in messages:
            received.append(self.socketB.receive())
        # Check all messages are received in order
        self.assertEqual(received, messages)

    def test_fifo_delivery_multiple_rounds(self):
        # Send msg1 in round 0, advance to round 1, send msg2
        self.socketA.send('msg1', 'B')
        self.clock.set(1)
        self.socketA.send('msg2', 'B')
        # Now, receive from B in rounds 1, 2
        self.clock.set(1)
        self.assertEqual(self.socketB.receive(), 'msg1')
        self.clock.set(2)
        self.assertEqual(self.socketB.receive(), 'msg2')
        self.clock.set(0)
        self.assertEqual(self.socketB.receive(), None)


if __name__ == '__main__':
    unittest.main()
