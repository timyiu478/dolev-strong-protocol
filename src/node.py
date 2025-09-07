from keygen import genKeyPair

from ca import Certificate
from history import History
from validator import Validator
from beacon import Beacon
from byzantine import FaultyBeacon
from executor import Executor

import threading


class Node:
    def __init__(self, id, peers, leader, isFixedLeader, clock, recordPattern,
                 historyFileName, f, sigManager, ca, network, isFaulty):
        pubKey, priKey = genKeyPair()
        cert = Certificate(id, pubKey)
        cert.sig = ca.sign(cert)

        socket = network.createSocket(id)

        self.history = History(historyFileName)
        self.validator = Validator(recordPattern, clock, ca, sigManager)
        self.beacon = None
        if isFaulty:
            self.beacon = FaultyBeacon(self.history, id, peers, leader, isFixedLeader, clock
                    , f, cert, priKey, self.validator, sigManager, socket, recordPattern)
        else:
            self.beacon = Beacon(self.history, id, peers, leader, isFixedLeader, clock, f
                        , cert, priKey, self.validator, sigManager, socket)
        self.executor = Executor(self.history, recordPattern)

    def run(self, stopEvent):
        beacon_thread = threading.Thread(target=self.beacon.run, args=(stopEvent,))
        executor_thread = threading.Thread(target=self.executor.run, args=(stopEvent,))

        beacon_thread.start()
        executor_thread.start()

        beacon_thread.join()
        executor_thread.join()

        self.history.save()
