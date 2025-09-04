from datetime import timedelta

from keygen import genKeyPair

from ca import CertAuthority
from sigManager import SigManager
from node import Node
from network import Network

import threading
import time


PEERS = [0, 1, 2, 3, 4]
F = 2
LEADER = 0
ROUNDTW = timedelta(seconds=8)
RECORDPATTERN = r"([+\-\*/]):(\d+)"
RECORDS = [
  "+:1",
  "-:1",
  "+:1",
  "*:9",
  "*:2",
  "/:18"
]


def main():
    sigMan = SigManager()
    net = Network(PEERS)
    caPubKey, caPriKey = genKeyPair()
    certAuth = CertAuthority(caPubKey, caPriKey, sigMan)
    nodes = {}
    nodeThreads = []
    stopEvent = threading.Event()

    for id in PEERS:
        node = Node(id, PEERS, LEADER, ROUNDTW, RECORDPATTERN
                , f"history/{id}.txt", F, sigMan, certAuth, net)
        nodes[id] = node
        nodeThreads.append(threading.Thread(target=node.run, args=(stopEvent,)))
        nodeThreads[-1].start()

    for record in RECORDS:
        nodes[LEADER].beacon.start(record)

    time.sleep(ROUNDTW.total_seconds() * (F + 2) * (len(RECORDS) + 1))

    stopEvent.set()

    for t in nodeThreads:
        t.join()


if __name__ == "__main__":
    main()
