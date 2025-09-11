'''
OVERVIEW
--------------------------------------------------------------------------------
Collects the sent DNS Packets by the client, finds the IP address using resolution
rules and logs the resolved IP address.

--------------------------------------------------------------------------------
DNS RESOLUTION RULES

IP Pool: [
"192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
"192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
"192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15"
]

Rules:
1. Extract timestamp from custom header: "HHMMSSID"
2. Apply these rules to the extracted header:
    a. Extract the hour from the timestamp to determine the time period.
    b. Use the ID and apply modulo 5 to get a specific IP.
    c. Select IP from appropriate pool segment

--------------------------------------------------------------------------------
'''

import socket
from scapy.layers.dns import DNS

PORT = 23
OUTPUT_FILE = "server_response.txt"

# IP pool
IP_POOL = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
    "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
    "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15"
]

def pick_ip(header):
    """Resolve IP based on Header"""
    try:
        hour = int(header[0:2])
        sid = int(header[6:8])
    except:
        return "192.168.1.1"  # default if parsing fails

    # Time Slot
    if 4 <= hour <= 11:      # morning
        ip_pool_start = 0
    elif 12 <= hour <= 19:   # afternoon
        ip_pool_start = 5
    else:                    # night
        ip_pool_start = 10

    # IP Number    
    ip_number = sid % 5
    index = ip_pool_start + ip_number
    return IP_POOL[index]

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))
    print(f"Server listening on port {PORT}...")
    print("Server Response")
    print("---------------------------------------------------------------------------------")
    print("Custom Header Value | Domain Name | Resolved IP Address")
    print("---------------------------------------------------------------------------------")

    # open file once, overwrite at start
    with open(OUTPUT_FILE, "w") as out:
        out.write("Custom Header Value | Domain Name | Resolved IP Address\n")
        out.write("-------------------------------------------------------\n")

    while True:
        data, addr = sock.recvfrom(4096)
        header = data[:8].decode(errors="ignore")
        dns_bytes = data[8:]

        qname = "unknown"
        try:
            qname = DNS(dns_bytes).qd.qname.decode()
        except:
            pass

        ip = pick_ip(header)
        reply = ip.encode()
        sock.sendto(reply, addr)

        line = f"{header} | {qname} | {ip}"
        print(line)
        

        with open(OUTPUT_FILE, "a") as out:
            out.write(line + "\n")


if __name__ == "__main__":
    main()
