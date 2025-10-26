from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSController
from mininet.link import TCLink

from scapy.utils import RawPcapReader
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.l2 import Ether
import re
import time
import os

DNSRESOLVER = "CUSTOM" #  "CUSTOM or DEFAULT"

class AssignmentTopo(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')
        dns = self.addHost('dns', ip='10.0.0.5') 

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        self.addLink(h1, s1, bw=100, delay='2ms')
        self.addLink(h2, s2, bw=100, delay='2ms')
        self.addLink(h3, s3, bw=100, delay='2ms')
        self.addLink(h4, s4, bw=100, delay='2ms')
        self.addLink(dns, s2, bw=100, delay='1ms')

        self.addLink(s1, s2, bw=100, delay='5ms')
        self.addLink(s2, s3, bw=100, delay='8ms')
        self.addLink(s3, s4, bw=100, delay='10ms')


def dns_analysis(net, host_domain_mapping):    
    for host_name, domain_file in host_domain_mapping.items():
        host = net.get(host_name)
        domains = []
        with open(f"{domain_file}.txt","r") as f:
            domains = f.readlines()
        
        if not domains:
            print(f"No domains to test for {host_name}. Skipping.")
            continue

        latencies = []
        success_count = 0
        fail_count = 0
        
        print(f"\nStarting DNS lookups for {len(domains)} domains...")
        start_time = time.time() 

        for domain in domains:
            domain = domain.strip()
            if not domain:
                continue
            
            if (DNSRESOLVER == "DEFAULT"):
                output = host.cmd(f'dig {domain} @8.8.8.8')
            else:
                output = host.cmd(f'dig {domain} @10.0.0.5 -p 53534')
            #print("---> Output is ", output)
            status_match = re.search(r"status: (\w+)", output)
            
            if status_match and status_match.group(1) == "NOERROR":
                success_count += 1
                latency_match = re.search(r"Query time: (\d+) msec", output)
                if latency_match:
                    latencies.append(int(latency_match.group(1)))
            else:
                fail_count += 1
        
        end_time = time.time() 
        total_time = end_time - start_time

        avg_latency = 0
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            
        avg_throughput = 0
        if total_time > 0:
            avg_throughput = success_count / total_time 

        print(f"Results for {host_name}:")
        print(f"    - Successfully Resolved: {success_count}")
        print(f"    - Failed Resolutions:    {fail_count}")
        print(f"    - Average Lookup Latency: {avg_latency:.2f} ms")
        print(f"    - Average Throughput:    {avg_throughput:.2f} queries/sec")


if __name__ == '__main__':
    domain_files = {
        'h1': 'PCAP_1_H1_domains',
        'h2': 'PCAP_2_H2_domains',
        'h3': 'PCAP_3_H3_domains',
        'h4': 'PCAP_4_H4_domains',
    }
    
    topo = AssignmentTopo()
    net = Mininet(topo=topo, link=TCLink, controller=OVSController)
    nat = net.addNAT()
    nat.configDefault()

    print("Starting network...")
    net.start()
    net.pingAll()
    #CLI(net)
    
    if (DNSRESOLVER == "CUSTOM"):
        dns_host = net.get('dns')

        # Start your resolver
        print("Starting custom DNS resolver on dns node...")
        dns_host.cmd('python3 /home/nimitt/CS331-CN-Assignments/A2/resolver.py &')
        time.sleep(3)

        # Update resolv.conf for all other hosts
        for h in ['h1', 'h2', 'h3', 'h4']:
            host = net.get(h)
            host.cmd('echo "nameserver 10.0.0.5" > /etc/resolv.conf')

    dns_analysis(net, domain_files)
    print(" Stopping network...")
    net.stop()