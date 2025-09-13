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
from scapy.all import PcapReader, DNS, UDP
import socket, time

# Globals
SERVER_IP = "127.0.0.1"
SERVER_PORT = 23
PCAP_FILE = "5.pcap"
LOCAL = False
OUTPUT_FILE = "client_ans.txt"

def make_header(seq):
    ''' return current time + seq number in bits '''
    ts = time.strftime("%H%M%S", time.localtime())
    return f"{ts}{seq:02d}".encode()

def main():
    ''' send DNS packets with header to server '''

    # reading pcap file
    pkts = PcapReader(PCAP_FILE)

    # creating a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # writing response received
    with open(OUTPUT_FILE, "w") as out:
        out.write("Custom Header Value | Domain Name | Resolved IP Address\n")
        out.write("-------------------------------------------------------\n")

        seq = 0

        for p in pkts:
            # Getting only DNS query and skipping mDNS 
            if p.haslayer(DNS) and p[DNS].qr == 0 and p[UDP].dport == 53 and not LOCAL:  
                qname = p[DNS].qd.qname.decode()                                        
                
                # if qname.endswith(".local.") and not LOCAL:   # other logic for skipping mDNS Queries
                #     continue

                # making header
                header = make_header(seq)
                payload = header + bytes(p[DNS])
                sock.sendto(payload, (SERVER_IP, SERVER_PORT))

                # receiving response from server
                try:
                    data, _ = sock.recvfrom(2048)
                    # resolved = data.decode()
                    resolved = DNS(data).an[0].rdata
                    
                except:
                    resolved = "No Reply"
                
                # logging to file
                line = f"{header.decode()} | {qname} | {resolved}"
                out.write(line + "\n")

                seq += 1
        out.write("-------------------------------------------------------\n")
        

if __name__ == "__main__":
    main()
