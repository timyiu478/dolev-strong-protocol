## Key Implementation Challenges

### 1. how to synchronous round between honest nodes when the leader can start the protocol at anytime

How we solve it:

1. only allowing leader to broadcast a message a round *0*. 
1. each node shares the same synchronous clock.
1. the network ensures message sent from round *i* can be received at round *i+1*.
