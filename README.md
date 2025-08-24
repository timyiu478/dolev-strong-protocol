# Dolev Strong protocol

## Assumptions

1. **Permissioned**: a prior known set of nodes $\{1, 2, 3, ..., n\}$.
1. **Public Key Infrastructure**: each node has a pair of $pk_i$, $sk_i$ where $pk_i$ is known to all nodes upfront.
1. **Synchronous Network**: 
    1. all nodes share a global clock, time steps from $0, 1, 2, ...$.
    1. the message sent from time $t$ will be arrived at time $t+1$ (in some arbitrary order).

## References

1. https://decentralizedthoughts.github.io/2019-12-22-dolev-strong/
1. https://www.cs.umd.edu/~jkatz/gradcrypto2/NOTES/lecture26.pdf
1. https://elaineshi.com/docs/blockchain-book.pdf
