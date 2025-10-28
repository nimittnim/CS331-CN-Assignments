## Part A:
mininet@mininet-vm:~/CS331-CN-Assignments/A2$ sudo python3 topology.py
No route found for IPv6 destination :: (no default route?)No route found for IPv6 destination :: (no default route?)Starting network...
*** Ping: testing ping reachability
dns -> h1 h2 h3 h4 nat0 
h1 -> dns h2 h3 h4 nat0 
h2 -> dns h1 h3 h4 nat0 
h3 -> dns h1 h2 h4 nat0 
h4 -> dns h1 h2 h3 nat0 
nat0 -> dns h1 h2 h3 h4 
*** Results: 0% dropped (30/30 received)

## Part B:
Starting socat proxy for default resolver...
Started socat proxy with PID: 22928
mininet> exit

Starting DNS lookups for 100 domains...
Results for h1:
    - Successfully Resolved: 76
    - Failed Resolutions:    24
    - Average Lookup Latency: 116.95 ms
    - Average Throughput:    3.94 queries/sec

Starting DNS lookups for 100 domains...
Results for h2:
    - Successfully Resolved: 71
    - Failed Resolutions:    29
    - Average Lookup Latency: 98.89 ms
    - Average Throughput:    2.93 queries/sec

Starting DNS lookups for 100 domains...
Results for h3:
    - Successfully Resolved: 72
    - Failed Resolutions:    28
    - Average Lookup Latency: 179.28 ms
    - Average Throughput:    3.66 queries/sec

Starting DNS lookups for 100 domains...
Results for h4:
    - Successfully Resolved: 77
    - Failed Resolutions:    23
    - Average Lookup Latency: 175.94 ms
    - Average Throughput:    3.57 queries/sec

Stopping socat proxy (PID: 22928)...
 Stopping network...
