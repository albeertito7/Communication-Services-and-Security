#!/bin/bash

file=$1

if [ $# -eq 0 ]
then
    echo "No file argument supplied. Must be specified the .pcapng file to be evaluated."
elif [ "${file##*.}" != "pcapng" ]
then
	echo "The extension of the file provided is not correct."
    echo "Must be a '.pcapng' file; the PCAP Next Generation file format, that is a standard format for storing captured data over the network."
    echo "Exiting ..."
    exit -1 
fi

echo "Processing $file file ..."

# -r | --read-file <infile>
# -T fields (set the format of the output when viewing decoded packet data)
# -e <field> (add a field to the list of fields to display)
# frame (wireshark frame number)
# -Y | --display-filter <displaY filter> (Packets matching the filter are printed or written to file)

time=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src == 11.0.0.1" -r captureP1.pcapng -T fields -e frame.time_relative | tail -1)

bytes_array=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src == 11.0.0.1" -r captureP1.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

echo ""
echo "Tap0 Precedence 7: $bytes Bytes"
#bits=$[$bytes*8]
avg_rate=$(bc <<< "$bytes/$time")
echo "Avg rate: $average_rate Bps"
echo ""

total_bytes=$bytes

bytes_array=$(tshark -Y "ip.dsfield.dscp == 8  and ip.src == 11.0.0.1" -r captureP1.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

echo ""
echo "Tap0 Precedence 1: $bytes Bytes"
#bits=$[$bytes*8]
avg_rate=$(bc <<< "$bytes/$time")
echo "Avg rate: $average_rate Bps"
echo ""

total_bytes=[$total_bytes + $bytes]