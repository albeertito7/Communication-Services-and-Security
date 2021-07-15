# Create    4 nodes
#
#   n0 (UDP)
#   \
#    \
#     n2 ---------------- n3
#    /
#   /
#  n1 (TCP)

# set => setting variable to a given value [$ns node]
# all between brackets [] is a command
# [$ns node] uses 'ns' simulator to create/build a node
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

# Link the nodes with duplex comms links
# duplex => the link works in both direcctions
# droptail => for a given link and an endpoint queue, everything that no fits into that queue is dropped
#          => so, is needed to specify the queue length on the intermediate node = n2
# usage: [$ns] [type] [endpoint1] [endpoint2] [transmission rate] [propagation delay (physical)] [policy to deal with the incomming packets]
$ns duplex-link $n0 $n2 5Mb 20ms DropTail
$ns duplex-link $n1 $n2 5Mb 20ms DropTail
$ns duplex-link $n2 $n3 1Mb 50ms DropTail

# once the links are created we should attach to the nodes the tcp agents
# every node should have an agent running, and every agent should have a traffic generator (CBR) (Constant Bit Rate Generator)
# like a stack:
#                 [CBR]
#                 [Agent]
#                 [Node]
#
# so, for n0 and n1, this will be the schema
# and for n2, will only require the [Node] layer because is an IP-Router
# and for n3, will require the [Node] layer and a kind of [TCP-Sink] or [UDP-Sink], as we only want to generate traffic in one direction (from n1,n2 to n3)

# Node 0; UDP agent with CBR traffic
# define a variable as an agent
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0 # attach n0 to udp0

set cbr0 [new Application/Traffic/CBR]
$cbr0 set rate_ 0.5Mbps # varialbes ending with undersocore are internal ns variables
$cbr0 attach-agent $udp0 # attach cbr to the agent
$udp 0 set class_ 0 # traffic flow identifier

# Node 1: TCP agent using Karn algorithm
# Change tcpTick timer default value
# With CBR traffic generator
set tcp0 [new Agent/TCP/RFC793edu]
$ns attach-agent $n1 $tcp0
$tcp0 set class_ 1

$tcp0 set add793karnrtt_ $karn
$tcp0 set add793jacobsonrtt_ $jacobson
$tcp0 set add793expbackoff_ true
$tcp0 set add793slowstart_ true
$tcp0 set tcpTick_ 0.01 # 0.01 sec = 10ms # time the simulator will sample all the simulation; the time between simulation samples/events

$set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.5Mbps
$cbr1 attach-agent $tcp0

# Node 3: 2 Sinks
set null0 [new Agent/Null] # sink for UDP traffic = NULL, because UDP is a non-connected protocol, so the only sink requirement is to get packets
$ns attach-agent $n3 $null0
set null1 [new Agent/TCPSink] # sink for TCP traffic, this sink must answer acknoledgements and so on, has to perform some actions
$ns attach-agent $n3 $null1

# Connect agents
$ns connect $udp0 null0
$ns connect $tcp0 null1

# The next point is to start, stop, and record the simulation

$ns at 5.0 "$cbr0 start"
$ns at 10.0 "$cbr0 stop"

$ns at 0.0 "$cbr1 start"
$ns at 0.0 "record" # executes a prodecure
$ns at 15.0 "finish"

# to record the info will be used to different files
set nf [open $file.tr w]
$ns trace-all $nf # put in the file descriptor $nf, all what happens inside the simulator (all the events)
set nff [open $file.rtt w] # 

proc record() {} {
    # some operations
    set rtt [expr [$tcp0 set rtt_] * [$tcp0 set tcpTick_]]
    set srtt [expr ([$tcp set srtt_] >> [$tcp0 set T_SRTT_BITS]) * [$tcp0 set tcpTick_]]
    set rttvar [expr ([$tcp0 set rttvar_] >> [$tcp0 set T_RTTVAR_BITS]) * [$tcp0 set tcpTick_]]
    set rto [expr [$tcp0 set rto_] * [$tcp0 set tcpTick_]]
    puts $nff "$now $rtt $srtt $rttvar $rto" # write/put specific info

    $ns at [expr $now+0.1] "record" # every 0.1 sec "record" procedure will be called to do some operations (get info from the simulations)
}

# Internal 'ns' variables end with '_'
# Some of them:
#   cwnd_ = cwnd
#   ssthresh = cwmax
#   window_ = CWMAX
#   maxcwnd_ = limit to cwnd # internal ns limit to cwnd

# One can access these variables throguh a tcp agent
# puts "Value of cwnd: [$tcp0 set cwnd_]"
# set rtt [expr [$tcp0 set rtt_] * [$tcp0 set tcpTick_]]
# set srtt [expr ([$tcp set srtt_] >> [$tcp0 set T_SRTT_BITS]) * [$tcp0 set tcpTick_]]
# set rttvar [expr ([$tcp0 set rttvar_] >> [$tcp0 set T_RTTVAR_BITS]) * [$tcp0 set tcpTick_]]
# set rto [expr [$tcp0 set rto_] * [$tcp0 set tcpTick_]]
# puts $nff "$now $rtt $srtt $rttvar $rto "

# T_SRTT_BITS = 3
# T_RTTVAR_BITS = 8