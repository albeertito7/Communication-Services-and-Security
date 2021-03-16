# Network Scheduling Algorithms
Script implementing the packet-based network scheduling algorithms called:
<ul>
    <li>Fair Queueing (FQ)</li>
    <li>Weighted Fair Queueing (WFQ)</li>
<ul>

## Arguments

Input:
<ul>
    <li>file based on a list of triplets where each one represents an arrival packet, the ones ordered in time, with the following fields:
        <ol><li>Arrival time (float)</li>
        <li>Packet size (float)</li>
        <li>Flow/stream identifier (integer >= 1)</li></ol>
    </li>            
    <li>In case of WFQ:
        <ul><li>Fraction of the bandwidth assigned to each flow (as a percentage). Comma separated. As an example: 50,10,40</li></ul>
    </li>
</ul>
