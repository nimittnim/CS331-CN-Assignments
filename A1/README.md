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
**Step 1.** Enter the "Task1" directory.

```
cd ./A1/"Task1"
```
Save the packet capture file x.pcap here and update it in client.py `PCAP_FILE=x.pcap`.

**Step 2.** Run the run.sh/run.bat file.
For Linux/Mac ->
```
chmod +x run.sh
./run.sh
```

For Windows ->
```
run.bat
```

**Output:**\
**run.sh** file will run **client.py** and **server.py**. The DNS resolution report will be printed on console and logged in **client_ans.txt** (Server response recieved by client) and **server_response.txt** (Server response).

**Remark:**\
1 Make sure no process is using the `PORT` in client.py and server.py. \
2 For sending local DNS packets (mDNS), set `LOCAL = TRUE` in client.py. \
3 For different machines update the server port and address in client.py.


### Task 2: Traceroute
*** Instructions ***
1 Find the packet capture file for executions in ./A1/Task2 \
2 For answers and execution refer to ./A1/report.pdf
