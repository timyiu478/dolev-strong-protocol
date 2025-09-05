from datetime import timedelta

from keygen import genKeyPair

from ca import CertAuthority
from sigManager import SigManager
from node import Node
from network import Network
from clock import Clock

import threading
import time


CLEARHISTORY = True
PEERS = [0, 1, 2, 3]
FAULTYNODES = [1, 2]
F = 2
LEADER = 0  # fixed leader mode
ROUNDTW = timedelta(seconds=4)
RECORDPATTERN = r"([+\-\*/]):(\d+)"
RECORDS = [
  "+:1",
  "-:2",
  "*:3",
  "/:4",
  "+:5",
  "-:6",
  "*:7",
  "/:8",
  "+:9",
]


def main():
    sigMan = SigManager()
    clock = Clock(ROUNDTW, F)
    net = Network(clock, PEERS, F)
    caPubKey, caPriKey = genKeyPair()
    certAuth = CertAuthority(caPubKey, caPriKey, sigMan)
    nodes = {}
    nodeThreads = []
    stopEvent = threading.Event()

    if CLEARHISTORY:
        for id in PEERS:
            with open(f"history/{id}.txt", "w"):
                pass

    # run network
    netThread = threading.Thread(target=net.run, args=(stopEvent,))
    netThread.start()

    for id in PEERS:
        isFaulty = True if id in FAULTYNODES else False
        node = Node(id, PEERS, LEADER, clock, RECORDPATTERN
                , f"history/{id}.txt", F, sigMan, certAuth, net, isFaulty)
        nodes[id] = node
        nodeThreads.append(threading.Thread(target=node.run, args=(stopEvent,)))
        nodeThreads[-1].start()

    for record in RECORDS:
        nodes[LEADER].beacon.start(record)

    time.sleep(ROUNDTW.total_seconds() * (F + 2) * (len(RECORDS) + 1))

    # check the honest nodes
    for id in PEERS:
        if id not in FAULTYNODES:
            reg = nodes[id].executor.register
            history = nodes[id].history.getHistory()
            print(f"Node {id}'s register value is {reg}")
            print(f"Node {id}'s history is {history}")

    stopEvent.set()

    for t in nodeThreads:
        t.join()
    netThread.join()


if __name__ == "__main__":
    main()
