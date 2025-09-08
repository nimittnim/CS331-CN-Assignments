'''
OVERVIEW
--------------------------------------------------------------------------------
Collects the sent DNS Packets by the client, Find the IP address using resolution
rules and Log the resolved IP address

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
import json
