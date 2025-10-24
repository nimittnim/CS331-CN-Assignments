```
NAT is by default DOWN. To turn it UP follow these commands:

$ sudo dhclient eth1

```


*** Ping: testing ping reachability
dns -> h1 h2 h3 h4 nat0 
h1 -> dns h2 h3 h4 nat0 
h2 -> dns h1 h3 h4 nat0 
h3 -> dns h1 h2 h4 nat0 
h4 -> dns h1 h2 h3 nat0 
nat0 -> dns h1 h2 h3 h4 
*** Results: 0% dropped (30/30 received)

Starting DNS lookups for 100 domains...
Results for h1:
    - Successfully Resolved: 76
    - Failed Resolutions:    24
    - Average Lookup Latency: 290.26 ms
    - Average Throughput:    2.76 queries/sec

Starting DNS lookups for 100 domains...
Results for h2:
    - Successfully Resolved: 72
    - Failed Resolutions:    28
    - Average Lookup Latency: 281.50 ms
    - Average Throughput:    2.63 queries/sec

Starting DNS lookups for 100 domains...
Results for h3:
    - Successfully Resolved: 71
    - Failed Resolutions:    29
    - Average Lookup Latency: 238.83 ms
    - Average Throughput:    2.96 queries/sec

Starting DNS lookups for 100 domains...
Results for h4:
    - Successfully Resolved: 77
    - Failed Resolutions:    23
    - Average Lookup Latency: 270.12 ms
    - Average Throughput:    3.10 queries/sec
 Stopping network...