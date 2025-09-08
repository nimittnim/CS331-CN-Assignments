'''
OVERVIEW
--------------------------------------------------------------------------------
Reads the PCAP file to extract DNS Packets, adds header to the DNS Packets and
send them to server.

--------------------------------------------------------------------------------
HEADER FORMAT
Size: 8 bytes
Contents: HHMMSSID
where
a. HH: hour in 24-hour format
b. MM: minute
c. SS: second
d. ID: Sequence of DNS query starting from 00
--------------------------------------------------------------------------------
'''

# Importing Libraries
import socket
from scapy.all import rdpcap


# Reading PCAP file
packets = rdpcap("5.pcap")
for pkt in packets:
    print(pkt.summary())
