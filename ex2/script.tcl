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
#

set ns [new Simulator]
set filename "sim-trace"
set nf [open $filename.tr w]
$ns trace-all $nf
set nff [open $filename.rtt w]

proc end {} {
    global ns nf nff
    $ns flush-trace
    close $nf
    close $nff
    exit 0
}

proc record {} {
    global ns tcp nff cbr
    set now [$ns now]

    for { set index 0 } { $index < [array size tcp] } { incr index } {
        set rtt  [expr [$tcp($index) set rtt_]  * [$tcp($index) set tcpTick_]]
        set srtt  [expr ([$tcp($index) set srtt_] >> [$tcp($index) set T_SRTT_BITS]) * [$tcp($index) set tcpTick_]]
        set rttvar  [expr ([$tcp($index) set rttvar_] >> [$tcp($index) set T_RTTVAR_BITS]) * [$tcp($index) set tcpTick_]]
        set bo [expr [$tcp($index) set backoff_]]
        set cwnd  [expr [$tcp($index) set cwnd_]]
        set cwmax  [expr [$tcp($index) set cwmax_]]
        puts $nff "$index $now $rtt $srtt $cwnd $cwmax [expr 0.5*($bo-1)]"
    }

    $ns at [expr $now+0.1] "record"
}

# scenario
set n(0) [$ns node]
set n(1) [$ns node]
set n(2) [$ns node]
set n(3) [$ns node]
set n(4) [$ns node]

set cbr(0) [new Application/Traffic/CBR]
set cbr(1) [new Application/Traffic/CBR]
set cbr(2) [new Application/Traffic/CBR]

set tcp(0) [new Agent/TCP]
set tcp(1) [new Agent/TCP/Reno]
set tcp(2) [new Agent/TCP/Vegas]

set null(0) [new Agent/TCPSink]
set null(1) [new Agent/TCPSink]
set null(2) [new Agent/TCPSink]

# Links
$ns duplex-link $n(0) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(1) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(2) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(3) $n(4) 1Mb 50ms DropTail

# Node0
$ns attach-agent $n(0) $tcp(0)
$cbr(0) set rate_ 0.5Mbps
$cbr(0) attach-agent $tcp(0)
$tcp(0) set class_ 0
$tcp(0) set tcpTick_ 0.01
$tcp(0) set add793slowstart_ true
$tcp(0) set cwmax_ 40

# Node1
$ns attach-agent $n(1) $tcp(1)
$cbr(1) set rate_ 0.5Mbps
$cbr(1) attach-agent $tcp(1)
$tcp(1) set class_ 1
$tcp(1) set tcpTick_ 0.01
$tcp(1) set add793slowstart_ true
$tcp(1) set cwmax_ 40

# Node2
$ns attach-agent $n(2) $tcp(2)
$cbr(2) set rate_ 0.5Mbps
$cbr(2) attach-agent $tcp(2)
$tcp(2) set class_ 2
$tcp(2) set tcpTick_ 0.01
$tcp(2) set add793slowstart_ true
$tcp(2) set cwmax_ 40
$tcp(2) set v_alpha_ 3
$tcp(2) set v_beta_ 6

# Node3
$ns queue-limit $n(3) $n(4) 20

# Node4
$ns attach-agent $n(4) $null(0)
$ns attach-agent $n(4) $null(1)
$ns attach-agent $n(4) $null(2)

$ns connect $tcp(0) $null(0)
$ns connect $tcp(1) $null(1)
$ns connect $tcp(2) $null(2)

$tcp(0) attach-trace $nff
$tcp(1) attach-trace $nff
$tcp(2) attach-trace $nff

# every hald sec CBR0
for { set index 0 }  { $index < 20 }  { incr index } {
    set end [expr {$index + 0.5}]
    $ns at $index "$cbr(0) start"
    $ns at $end "$cbr(0) stop"
    # puts "Starting n0 at $index and stopping it at $end"
}

# every sec CBR1
for { set index 0 }  { $index < 20 }  { incr index 2 } {
    set end [expr {$index + 1}]
    $ns at $index "$cbr(1) start"
    $ns at $end "$cbr(1) stop"
    # puts "Starting n1 at $index and stopping it at $end"
}

# every 2 sec CBR2
for { set index 0 }  { $index < 20 }  { incr index 4 } {
    set end [expr {$index + 2}]
    $ns at $index "$cbr(2) start"
    $ns at $end "$cbr(2) stop"
    # puts "Starting n2 at $index and stopping it at $end"
}

# set procedures init time
$ns at 0.0 "record"
$ns at 20.0 "end"

# init simulation
$ns run