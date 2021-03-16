# Network Scheduling Algorithms
Script implementing the packet-based network scheduling algorithms called:
<ul>
    <li>Fair Queueing (FQ)</li>
    <li>Weighted Fair Queueing (WFQ)</li>
<ul>

# Arguments

Input:
    ■ file based on a list of triplets where each one represents an arrival packet, the ones ordered in time, with the following fields:
        - Arrival time (float)
        - Packet size (float)
        - Flow/stream identifier (integer >= 1)

        As an example:      0.1 1.0 1
                            0.2 2.1 2
                            ...
                     
    ■ In case of WFQ:
        - Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40
