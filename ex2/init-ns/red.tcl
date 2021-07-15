if {$argc == 1 } {
    set mode   [lindex $argv 0] 
    if {$mode == "false" ||  $mode == "true"   } {
    	puts "RED  Wait $mode"
    } else {
        puts "  Usage: ns $argv0 RED_Wait (true|false) "
        exit 1
   }
} else {
     puts "  Usage: ns $argv0 RED_Wait (true|false) "
    exit 1
}



# Creating the simulator object
set ns [new Simulator]

#file to store results
set nf [open sor.tr w]
$ns trace-all $nf

set nff [open sor.cw w]

#Finishing procedure
proc finish {} {
        global ns nf nff qmon
        $ns flush-trace
	# Process "sor.tr" to get sent packets
	exec awk {{ if ($1=="-" && $3==2 && $4==3) print $2, 21}}  sor.tr > tx
	# Process "sor.tr" to get dropped packets
	exec awk {{ if ($1=="d" && $3==2 && $4==3) print $2, 21}}  sor.tr > drop
        close $nf
        close $nff

	puts "Sent:  [$qmon set pdepartures_]"
	puts "Lost:  [$qmon set pdrops_]"

        exit 0
}


proc record { } {
	global ns  nff qmon
	set now [$ns now]
	puts $nff "$now  [$qmon  set pkts_]"

	$ns at [expr $now+0.1] "record"
}

#Create 4 nodes
#
#  n0
#  \
#   \
#    n2--------n3
#   /
#  /
# n1
 
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

#Duplex lines between nodes
$ns duplex-link $n0 $n2 5Mb 20ms DropTail
$ns duplex-link $n1 $n2 5Mb 20ms DropTail


#Creem  RED line

$ns duplex-link $n2 $n3 0.7Mb 50ms RED
set cua [[$ns link $n2 $n3] queue]

$cua set bytes_ false
$cua set queu-in-bytes_ false
$cua set thresh_ 10
$cua set maxthresh_ 20
$cua set q_weight_ 0.5
$cua set wait_ $mode
$cua set linterm_ 50

#Monitoring line 2->3
set qmon [$ns monitor-queue $n2 $n3 ""]

# Node 0:  TCP agent with  FTP traffic
set tcp0 [new Agent/TCP]
$ns attach-agent $n0 $tcp0
set ftp0 [new Application/FTP]
$ftp0 set rate_ 0.5Mbps
$ftp0 attach-agent $tcp0
$tcp0 set class_ 1

set null0 [new Agent/TCPSink]
$ns attach-agent $n3 $null0


$ns connect $tcp0 $null0
$ns at 0.0 "$ftp0 start"
#$ns at 5.0 "$ftp0 stop"
#$ns at 10.0 "$ftp0 start"
#$ns at 15.0 "$ftp0 stop"


# TCP agent. Modifify default tcpTick  time(default 0.5 s)

set tcp1 [new Agent/TCP]

$tcp1 set class_ 1

$ns attach-agent $n1 $tcp1
$tcp1 set tcpTick_ 0.01


set null1 [new Agent/TCPSink]
$ns attach-agent $n3 $null1


# Add a  FTP  traffic generator
set ftp1 [new Application/FTP]
$ftp1 set rate_ 0.5Mbps
$ftp1 attach-agent $tcp1
$ns at 0.0 "$ftp1 start"
$ns at 0.0 "record"

$ns connect $tcp1 $null1 

# Stop simulation at  20 s.
$ns at 20. "finish"


#Run simulation
$ns run
