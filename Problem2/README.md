# Network Scheduling Algorithms
Script implementing the packet-based network scheduling algorithms called:
* Fair Queueing (FQ)
* Weighted Fair Queueing (WFQ)


## Arguments

Input:
<ul>
    <li>File based on a list of triples sorted in time where each one represents a packet with the following fields:
        <ol type="1">
            <li>Arrival time (float)</li>
            <li>Packet size (float)</li>
            <li>Flow/stream identifier (integer >= 1)</li>
        </ol>
    </li>
    <li>In case of WFQ:
        <ul>
            <li>Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40</li>
        </ul>
    </li>
</ul>

Output:
    <ul>
        <li>The transmission order sequence according to the algorithm selected</li>
    </ul>
