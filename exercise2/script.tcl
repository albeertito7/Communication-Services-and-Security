# Create    5 nodes
#
#      CBR2 - n2 (TCP Vegas)
#                           \
#                            \
#                             \
#  CBR1- n1 (TCP Reno) ------- n3 -------- n4
#                              /
#                             /
#                            /
#       CBR0 - n0 (TCP Tahoe)


set ns [new Simulator]

set nf [open $ex.tr w]
$ns trace-all $nf
set nff [open $ex.rtt w]

proc terminate() {} {
    global ns nf nff
    $ns flush-trace
    close $nf
    close $nff
    exit 0
}

proc record() {} {
    $ns at [expr $now+0.1] "record"
}

# Config Scenario
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]

# Links
$ns duplex-link $n0 $n3 5Mb 20ms DropTail
$ns duplex-link $n1 $n3 5Mb 20ms DropTail
$ns duplex-link $n2 $n3 1Mb 50ms DropTail
$ns duplex-link $n3 $n4 1Mb 50ms DropTail

# Node0
set tcp0 [new Agent/TCP] # TCP Tahoe
$ns attach-agent $n0 $tcp0

set cbr0 [new Application/Traffic/CBR]
$cbr0 set rate_ 0.5Mbps # varialbes ending with undersocore are internal ns variables
$cbr0 attach-agent $tcp0 # attach cbr to the agent
$tcp0 set class_ 0 # traffic flow identifier
$tcp0 set tcpTick_ 0.01
$tcp0 set add793slowstart_ true
$tcp0 set cwmax_ 40

# Node1
set tcp1 [new Agent/TCP/Reno] # TCP Reno
$ns attach-agent $n1 $tcp1

set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.5Mbps # varialbes ending with undersocore are internal ns variables
$cbr1 attach-agent $tcp1 # attach cbr to the agent
$tcp1 set class_ 1 # traffic flow identifier
$tcp1 set tcpTick_ 0.01
$tcp1 set add793slowstart_ true
$tcp1 set cwmax_ 40

# Node2
set tcp2 [new Agent/TCP/Vegas] # TCP Vegas
$ns attach-agent $n2 $tcp2

set cbr2 [new Application/Traffic/CBR]
$cbr2 set rate_ 0.5Mbps # varialbes ending with undersocore are internal ns variables
$cbr2 attach-agent $tcp2 # attach cbr to the agent
$tcp2 set class_ 2 # traffic flow identifier
$tcp2 set tcpTick_ 0.01
$tcp2 set add793slowstart_ true
$tcp2 set cwmax_ 40
#$tcp1 set v_alpha_ 3
#$tcp1 set v_beta_ 6

# Node3
#$ns queue-limit $n(0) $n(3) 20
#$ns queue-limit $n(1) $n(3) 20
#$ns queue-limit $n(2) $n(3) 20
$ns queue-limit $n3 $n4 20

# Node4
set null0 [new Agent/TCPSink]
set null1 [new Agent/TCPSink]
set null2 [new Agent/TCPSink]
$ns attach-agent $n4 $null0
$ns attach-agent $n4 $null1
$ns attach-agent $n4 $null2

$ns connect $tcp0 $null0
$ns connect $tcp1 $null1
$ns connect $tcp2 $null2

$tcp0 attach-trace $nff
$tcp1 attach-trace $nff
$tcp2 attach-trace $nff

# Config Simulation
# Every half sec CBR0
for { set index 0 }  { $index < 20 }  { incr index } {
    set end [expr {$index + 0.5}]
    $ns at $index "$cbr0 start"
    $ns at $end "$cbr0 stop"
    # puts "Starting n0 at $index and stopping it at $end"
}

# Every sec CBR1
for { set index 0 }  { $index < 20 }  { incr index 2 } {
    set end [expr {$index + 1}]
    $ns at $index "$cbr1 start"
    $ns at $end "$cbr1 stop"
    # puts "Starting n2 at $index and stopping it at $end"
}

# Every 2 sec CBR2
for { set index 0 }  { $index < 20 }  { incr index 4 } {
    set end [expr {$index + 2}]
    $ns at $index "$cbr2 start"
    $ns at $end "$cbr2 stop"
    # puts "Starting n1 at $index and stopping it at $end"
}

$ns at 0.0 "record"
$ns at 20.0 "finish"

# Init Simulation
$ns run