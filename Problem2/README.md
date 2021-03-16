# Network Scheduling Algorithms
Script implementing the packet-based network scheduling algorithms called:
* Fair Queueing (FQ)
* Weighted Fair Queueing (WFQ)


## Arguments

Input:
* File based on a list of triples sorted in time where each one represents a packet with the following fields:
  1. Arrival time (float)
  2. Packet size (float)
  3. Flow/stream identifier (integer >= 1)

* In case of WFQ:
  - Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40</li>

Output:
* The transmission order sequence according to the algorithm selected</li>

