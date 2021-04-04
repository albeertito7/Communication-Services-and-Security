"""
ICT Project: Communication Services and Security
Exercise 2
Albert Pérez Datsira
Jeongyun Lee
"""

import sys, os
import pandas as pd
import matplotlib.pyplot as plt
from logger import Logger

sys.stdout = Logger("logProcessDataScript") # redirect stdout to create a log file

# process sim-trace.tr
header = ['Event_Type', 'Time', 'Src_Node', 'Dst_Node', 'Pckt_Type', 'Pckt_Size', 'Flags', 'Flow_Identifier', 'Src_Address', 'Dst_Address', 'Pckt_Number', 'Pckt_Identifier']
df = pd.read_csv('sim-trace.tr', sep=' ', names = header)

print(df.head().to_string(), "\n")
df.info()

# Lost Packets
lost_pckts = df.Event_Type == 'd' # get lots packets by mapping those ones with event_type == 'd' (dropped)
ids = df[lost_pckts].Flow_Identifier # filter by the flow_identifier (class)
# we could also filter by Src_Address, as we need the packets dropped by the n3

n0_lost = sum(ids == 0) # TCP Tahoe
n1_lost = sum(ids == 1) # TCP Reno
n2_lost = sum(ids == 2) # TCP Vegas

print("-"*os.get_terminal_size().columns)
print("Lost Packets")
print("Node 0, TCP Tahoe:\t", n0_lost)
print("Node 1, TCP Reno:\t", n1_lost)
print("Node 2, TCP Vegas:\t", n2_lost)
print("Total: ", ids.count())

# Transferred bytes
def mapNode(row, node):
  return row.Src_Node == int(node) and row.Event_Type == '-' # mapping condition

n0_pckts = df.apply(mapNode, axis = 1, args=('0'))
n1_pckts = df.apply(mapNode, axis = 1, args=('1'))
n2_pckts = df.apply(mapNode, axis = 1, args=('2'))
n3_pckts = df.apply(mapNode, axis = 1, args=('3'))
n4_pckts = df.apply(mapNode, axis = 1, args=('4'))

n0_bytes = sum(df[n0_pckts].Pckt_Size)
n1_bytes = sum(df[n1_pckts].Pckt_Size)
n2_bytes = sum(df[n2_pckts].Pckt_Size)
n3_bytes = sum(df[n3_pckts].Pckt_Size)
n4_bytes = sum(df[n4_pckts].Pckt_Size)
total_bytes = n0_bytes + n1_bytes + n2_bytes + n3_bytes + n4_bytes

print("-"*os.get_terminal_size().columns)
print("Transferred bytes:")
print("Node 0, TCP Tahoe:\t", n0_bytes)
print("Node 1, TCP Reno:\t", n1_bytes)
print("Node 2, TCP Vegas:\t", n2_bytes)
print("Node 3:\t", n3_bytes)
print("Node 4:\t", n4_bytes)
print("Total Agents:\t", n0_bytes + n1_bytes + n2_bytes)
print("Total Scenario:\t", total_bytes)
print("-"*os.get_terminal_size().columns)

# process sim-trace.rtt
header2 = ['Node', 'Time', 'rtt', 'srtt', 'cwnd', 'cwmax', 'bo'] # values collected
df2 = pd.read_csv('sim-trace.rtt', sep=' ', names = header2)

print(df2.head().to_string(), "\n")
df2.info()

# get cwnd values
cwnd0 = df2[df2.Node == 0].cwnd
cwnd1 = df2[df2.Node == 1].cwnd
cwnd2 = df2[df2.Node == 2].cwnd
time = df2[df2.Node == 0].Time

plt.plot(time, cwnd0, label='TCP Tahoe', color='blue')
plt.plot(time, cwnd1, label='TCP Reno', color='green')
plt.plot(time, cwnd2, label='TCP Vegas', color='red')

plt.title('Congestion window x Time')
plt.xlabel('Time (s)')
plt.ylabel('Congestion window (MSS)')
plt.legend(loc='upper right')
plt.savefig("cwnd-plot.png")
plt.show()