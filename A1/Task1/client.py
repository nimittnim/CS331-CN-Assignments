'''
OVERVIEW
--------------------------------------------------------------------------------
Reads the PCAP file to extract DNS Packets, adds header to the DNS Packets and
sends them to the server.

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
from scapy.all import rdpcap, DNS
import socket, time

# Globals
SERVER_IP = "127.0.0.1"
SERVER_PORT = 23
PCAP_FILE = "5.pcap"
LOCAL = False
OUTPUT_FILE = "client_ans.txt"

def make_header(seq):
    # add time and seq number
    ts = time.strftime("%H%M%S", time.localtime())
    return f"{ts}{seq:02d}".encode()

def main():
    pkts = rdpcap(PCAP_FILE)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # open file once, overwrite on each run
    with open(OUTPUT_FILE, "w") as out:
        out.write("Custom Header Value | Domain Name | Resolved IP Address\n")
        out.write("-------------------------------------------------------\n")

        seq = 0

        for p in pkts:
            if p.haslayer(DNS) and p[DNS].qr == 0:  # DNS query
                qname = p[DNS].qd.qname.decode()
                if qname.endswith(".local.") and not LOCAL:   # skip mDNS Queries
                    continue

                header = make_header(seq)
                payload = header + bytes(p[DNS])
                sock.sendto(payload, (SERVER_IP, SERVER_PORT))

                try:
                    data, _ = sock.recvfrom(2048)
                    resolved = data.decode()
                except:
                    resolved = "No Reply"

                line = f"{header.decode()} | {qname} | {resolved}"
                out.write(line + "\n")

                seq += 1
        out.write("-------------------------------------------------------\n")
        

if __name__ == "__main__":
    main()
