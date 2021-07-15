#!/bin/bash

display_usage()
{
    echo -e "\nusage: $0 [options] <infile>"
    echo -e "\nShell script that computes from the capture frame infile the total Bytes transmitted and the average rate in Bytes per second (Bps) for the following traffic flows:"
    echo  "   * From 11.0.0.1 with precedence 7"
    echo  "   * From 11.0.0.1 with precedence 1"
    echo  "   * From 12.0.0.1"
    echo -e "\nrequired arguments:"
    echo  "   infile:         Must be a .pcap or .pcapng file"
    echo -e "\noptional arguments:"
    echo  "   -h, --help      Shows usage message to provide help"
} 

file=$1


if [ $# -eq 0 ]
then
    echo "error: No infile argument supplied."
    display_usage
    exit 1
elif [[ ( $* == "--help") ||  $* == "-h" ]] 
then 
    display_usage
    exit 0
elif [[ "${file##*.}" != "pcapng" && "${file##*.}" != "pcap" ]]
then
    echo "error: The extension of the file provided is not correct."
    display_usage
    exit 2
fi

echo "Processing $file file ..."

# -r | --read-file <infile>
# -T fields (set the format of the output when viewing decoded packet data)
# -e <field> (add a field to the list of fields to display)
# frame (wireshark frame number)
# -Y | --display-filter <displaY filter> (Packets matching the filter are printed or written to file)

get_bytes()
{
    bytes_arraw=$1
    bytes=0
    for x in ${bytes_array[*]}; do
	    bytes=$[ $bytes + $x ];
    done
    echo $bytes
}

process()
{
    echo -e "\n$1: $2 Bytes"
    avg_rate=$(bc <<< "$2/$time")
    echo -e "Avg rate: $avg_rate Bps\n"
}

time=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src == 11.0.0.1" -r $file -T fields -e frame.time_relative | tail -1)

bytes_array=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src == 11.0.0.1" -r $file -T fields -e frame.len)
bytes=$(get_bytes $bytes_array)
process "Tap0 IP Precedence 7" $bytes
total_bytes=$bytes

bytes_array=$(tshark -Y "ip.dsfield.dscp == 8  and ip.src == 11.0.0.1" -r $file -T fields -e frame.len)
bytes=$(get_bytes $bytes_array)
process "Tap0 IP Precedence 1" $bytes
total_bytes=$[$total_bytes + $bytes]

bytes_array=$(tshark -Y "ip.src == 12.0.0.1" -r $file -T fields -e frame.len)
bytes=$(get_bytes $bytes_array)
process "Tap1 IP Without Precedence" $bytes
total_bytes=$[$total_bytes + $bytes]

echo -e "\nTotal bytes: $total_bytes Bytes\n"
