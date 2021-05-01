#!/bin/bash

# ICT Project: Communication Services and Security
# Exercise 4 Problem 1 Part 1
# Albert Pérez Datsira

display_usage() {
	echo -e "\nusage: $0 [options] <infile>"
    echo -e "\nShell script that computes from the capture frame infile the bits rate at each second"
    echo -e "\nrequired arguments:"
    echo  "   infile:         Must be a .pcap or .pcapng file"
    echo -e "\noptional arguments:"
	echo  "   -o, --out       Output name .csv file. By default will be 'output'"
    echo  "   -h, --help      Shows usage message to provide help"
}

infile=$1
outfile="output.csv"

if [ $# -eq 0 ]
then
    echo "error: No infile argument supplied."
    display_usage
    exit 1
elif [[ ( $* == "--help") ||  $* == "-h" ]] 
then 
    display_usage
    exit 0
elif [[ "${infile##*.}" != "pcapng" && "${infile##*.}" != "pcap" ]]
then
    echo "error: The extension of the file provided is not correct."
    display_usage
    exit 2
fi

if [ ! -z "$2" ]
then
	outfile="$2.csv" 
fi

# -r | --read-file <infile>
# -T fields (set the format of the output when viewing decoded packet data)
# -e <field> (add a field to the list of fields to display)
# frame (wireshark frame number)
# -Y | --display-filter <displaY filter> (Packets matching the filter are printed or written to file)

rate() {
	infile=$1
	outfile=$2

	times=$( tshark -Y "ip.src==14.0.0.1" -r "$infile" -T fields -e frame.time_relative) # look 14.0.0.1 is used as the topology has a NAT configured
	time=(${times// / })

	bytes_arrays=$(tshark -Y "ip.src==14.0.0.1" -r "$infile" -T fields -e frame.len)
	bytes_array=(${bytes_arrays// / })

	echo "time,bytes,rate" | tee "$outfile" # CSV headers

	tlen=${#time[@]} # how many records?

	for ((current_time=last_time=bytes=rate=0, i=0; i < $tlen; i++)) do
		bytes=$(bc <<< "${bytes_array[$i]}+$bytes") # accumulative bytes expression over time
		current_time=${time[$i]} # getting curren ttime
		dif=$(bc <<< "$current_time-$last_time>=1.0") # if differs more than 1 sec

		if [ "$dif" -eq "1" ]; then
			bits=$((bytes*8))
			rate=$(bc <<< "($bits/($current_time-$last_time))")
			echo "$current_time,$bits,$rate" | tee -a "$outfile"
			bytes=0
			last_time=$current_time
		fi
	done
}

echo -e "Processing $infile file ...\n"
rate $infile $outfile
