# Network Scheduling Algorithms
Script implementing the packet-based network scheduling algorithms called:
* Fair Queueing (FQ)
* Weighted Fair Queueing (WFQ)


## IO

Input:
* File based on a list of triples sorted in time where each one represents a packet with the following fields:
  1. Arrival time (float)
  2. Packet size (float)
  3. Flow/stream identifier (integer >= 1)

* In case of WFQ is specified:
  - Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40</li>

Output:
* The transmission order sequence according to the algorithm selected</li>

## Arguments
`usage: script.py [-h] [-s {FQ,WFQ}] [-f FLOWS] [-o OUTFILE] [-v] file`

```
positional arguments:
  file         File name containing the list of triplets to be scheduled.

optional arguments:
  -h, --help   show this help message and exit
  -s {FQ,WFQ}  String to specify the network scheduling algorithm policy. If not specified will be executed the Fair Queueing as a default option.
                  · FQ = Fair Queueing
                  · WFQ = Weighted Fair Queueing.
  -f FLOWS     Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40
               Will only be taken into account when the policy {WFQ} is specified.
  -o OUTFILE   Output file name containing the results
  -v           Display additional details about the execution such as the packets received and delivered at each time.
```


