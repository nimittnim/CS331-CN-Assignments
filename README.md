# CS331-CN-Assignments

## Overview

This is the Assignments Repository for CS 331, Computer Networks, Fall 2025.

Team Members:
| Name             | Roll No.   |
|------------------|------------|
| Nimitt           | 22110169   |
| Tapananshu Manoj | 22110270   |

## Assignment 1 Instructions
Access the Assignment 1 in ./A1

### Task 1: DNS Resolver
**Requirements:**\
Socket and scapy python packages.

**Instructions:**\
**Step 0:** Clone this repository.
```
git clone https://github.com/nimittnim/CS331-CN-Assignments
```
**Step 1.** Enter the "1. DNS" directory.

```
cd ./A1/"1. DNS"
```

**Step 2.** Run the run.sh file.
```
chmod +x run.sh
./run.sh
```

**Output:**\
**run.sh** file will run **client.py** and **server.py**. The DNS resolution report will be printed on console and logged in **client_ans.txt** (Server response recieved by client) and **server_response.txt** (Server response).

**Remark:**\
1 For sending local DNS packets (mDNS), set `LOCAL = TRUE` in client.py. \
2 Make sure no process is using the `PORT` in client.py and server.py.

### Task 2: Traceroute