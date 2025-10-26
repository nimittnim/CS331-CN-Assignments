import socket
import time
import threading
import struct
import logging
import json
from collections import namedtuple
from dns import message, rdatatype, exception
import dns.name
import dns.rdatatype
import dns.exception
import random  
import concurrent.futures  

# pip install dnspython
# Root servers list (hardcoded, IPv4)
ROOT_SERVERS = [
    "198.41.0.4",     # a.root-servers.net
    "199.9.14.201",   # b
    "192.33.4.12",    # c
    "199.7.91.13",    # d
    "192.203.230.10", # e
    "192.5.5.241",    # f
    "192.112.36.4",   # g
    "198.97.190.53",  # h
    "192.36.148.17",  # i
    "192.58.128.30",  # j
    "193.0.14.129",   # k
    "199.7.83.42",    # l
    "202.12.27.33"    # m
]

LOGFILE = "resolver_log_D.jsonl"
ENABLE_CACHE = False
PORT = 53534
MAX_WORKERS = 100  

# simple cache entry
CacheEntry = namedtuple("CacheEntry", ["answer_rrsets", "expiry"])

cache = {}
cache_lock = threading.Lock()  # <-- ADDED for thread-safety

# Clear the log file at startup
with open(LOGFILE, "w") as f:
    f.truncate(0)

# simple logger for JSON lines
logger = logging.getLogger("resolver")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOGFILE)
fh.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(fh)


def cache_get(qname, qtype_str):
    key = (str(qname).lower(), qtype_str)
    if not ENABLE_CACHE:
        return None, "MISS"
    
    with cache_lock:  # <-- ADDED thread-safety
        if key in cache:
            entry = cache[key]
            if time.time() < entry.expiry:
                return entry.answer_rrsets, "HIT"
            else:
                del cache[key]  # Expired
    return None, "MISS"

def cache_set(qname, qtype_str, answer_rrsets, ttl):
    if not ENABLE_CACHE or ttl <= 0:
        return
    key = (str(qname).lower(), qtype_str)
    expiry = time.time() + ttl
    
    with cache_lock:  # <-- ADDED thread-safety
        cache[key] = CacheEntry(answer_rrsets=answer_rrsets, expiry=expiry)


def log_record(record: dict):
    # write a json-line
    logger.info(json.dumps(record))


def query_server(qname, qtype, server_ip, timeout=2.0):
    """
    Send a DNS query (non-recursive) to server_ip and return (response, rtt)
    """
    # qtype is a string 'A', 'NS', etc.
    q = message.make_query(qname, qtype, want_dnssec=False)
    q.flags &= ~dns.flags.RD  # clear recursion desired -> iterative request
    wire = q.to_wire()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    start = time.time()
    try:
        s.sendto(wire, (server_ip, 53))
        data, _ = s.recvfrom(4096)
        rtt = (time.time() - start)
        resp = message.from_wire(data)
        return resp, rtt
    except Exception as e:
        return None, None
    finally:
        s.close()


def iterative_resolve(qname, qtype_str):
    """
    Perform iterative resolution; return final answer (or None) and a trace list.
    Trace element: dict with server_ip, step, response_summary, rtt
    """
    # cache check
    cached_rrsets, status = cache_get(qname, qtype_str)
    if cached_rrsets:
        return cached_rrsets, True, [{"cache_status": "HIT"}], 0.0, "CACHE"

    trace = []
    total_start = time.time()

    # start with root servers
    servers_to_try = list(ROOT_SERVERS)
    
    # Keep track of servers we've already queried for this name
    # to avoid simple loops.
    queried_servers = set()

    while True:
        if not servers_to_try:
            # failed to resolve
            total_time = time.time() - total_start
            return None, False, trace, total_time, "FAILED"

        server = servers_to_try.pop(0)
        
        if server in queried_servers:
            continue # Avoid re-querying same server
        queried_servers.add(server)

        resp, rtt = query_server(qname, qtype_str, server)
        
        rec = {
            "server_ip": server,
            "rtt": rtt if rtt is not None else -1,
            "step": "Query",
            "response": None
        }
        if resp is None:
            rec["response"] = "NO RESPONSE"
            trace.append(rec)
            continue

        # summarize response
        if resp.answer:
            # Got an answer
            ans_summary = [str(rr) for rr in resp.answer]
            rec["response"] = "ANSWER: " + ";".join(ans_summary)
            rec["step"] = "Authoritative/Answer"
            trace.append(rec)

            # --- MINOR FIX (TTL logic) ---
            # Find the minimum TTL in the answer set to use for caching
            min_ttl = None
            for rrset in resp.answer:
                if min_ttl is None or rrset.ttl < min_ttl:
                    min_ttl = rrset.ttl
            ttl_to_cache = min_ttl if min_ttl is not None else 30 # Default 30s
            
            cache_set(qname, qtype_str, resp.answer, ttl_to_cache)
            total_time = time.time() - total_start
            return resp.answer, True, trace, total_time, "ANSWER"
        
        else:
            # No answer: This is a referral
            auth = resp.authority
            addl = resp.additional
            rec["response"] = {
                "authority": [str(x) for x in auth] if auth else [],
                "additional": [str(x) for x in addl] if addl else []
            }
            trace.append(rec)

            if auth:
                for rrset in auth:
                    if rrset.rdtype == rdatatype.NS:
                        cache_set(rrset.name, "NS", [rrset], rrset.ttl)
            if addl:
                for rrset in addl:
                    # Cache glue records
                    if rrset.rdtype == rdatatype.A or rrset.rdtype == rdatatype.AAAA:
                        cache_set(rrset.name, rdatatype.to_text(rrset.rdtype), [rrset], rrset.ttl)

            # Pick IPs from additional (glue) as next servers
            next_servers = []
            if addl:
                for rr in addl:
                    for item in rr:
                        try:
                            if item.rdtype == rdatatype.A:
                                next_servers.append(item.to_text())
                        except Exception:
                            pass
            
            if next_servers:
                # We have glue! Add these servers to the front of the list.
                servers_to_try = list(set(next_servers)) + servers_to_try # Use set to de-dupe
                continue
            else:
                # No glue. We must resolve the NS names.
                ns_names = []
                if auth:
                    for rr in auth:
                        for item in rr:
                            try:
                                if item.rdtype == rdatatype.NS:
                                    ns_names.append(item.to_text())
                            except Exception:
                                pass
                
                derived_ips = []
                for ns_name_str in ns_names:
                    # Resolve the NS name's IP address. This is the crucial fix.
                    # We call ourselves to resolve the 'A' record for the nameserver.
                    # Note: We pass the string representation of the name.
                    ns_answer_rrsets, ns_success, ns_trace, _, _ = iterative_resolve(ns_name_str, 'A')
                    
                    trace.append({"step": "Sub-Resolve NS", "name": ns_name_str, "success": ns_success})

                    if ns_success and ns_answer_rrsets:
                        for rrset in ns_answer_rrsets:
                            if rrset.rdtype == rdatatype.A:
                                for item in rrset:
                                    derived_ips.append(item.to_text())
                
                if derived_ips:
                    servers_to_try = list(set(derived_ips)) + servers_to_try
                    continue
                else:
                    # No next servers, and couldn't resolve NS names. Fail.
                    total_time = time.time() - total_start
                    return None, False, trace, total_time, "NOREFERRAL"
                # --- END CRITICAL "NO GLUE" FIX ---



def handle_query(data, addr, sock):
    try:
        req = message.from_wire(data)
        qname = req.question[0].name
        qtype_int = req.question[0].rdtype
        qtype_str = dns.rdatatype.to_text(qtype_int)
    except Exception as e:
        return # Malformed query

    timestamp = time.time()
    log_base = {
        "timestamp": timestamp,
        "client_ip": addr[0],
        "query_name": str(qname),
        "query_type": qtype_str
    }

    answer_rrsets, success, trace, total_time, disposition = iterative_resolve(qname, qtype_str)
    
    servers_contacted = [t.get("server_ip") for t in trace if "server_ip" in t]

    cache_status = "HIT" if trace and trace[0].get("cache_status") == "HIT" else "MISS"

    record = {
        **log_base,
        "resolution_mode": "Iterative",
        "servers_contacted": list(set(servers_contacted)), # de-dupe
        "trace": trace,
        "total_time": total_time,
        "success": success,
        "cache_status": cache_status,
        "final_disposition": disposition
    }
    log_record(record)

    # Craft response
    resp_msg = message.make_response(req)
    if answer_rrsets:
        for rrset in answer_rrsets:
            try:
                resp_msg.answer.append(rrset)
            except Exception:
                pass # Should not happen
    else:
        resp_msg.set_rcode(2)  # SERVFAIL

    resp_bytes = resp_msg.to_wire()
    sock.sendto(resp_bytes, addr)


def udp_server(bind_ip="0.0.0.0", bind_port=PORT):

    # Use a fixed thread pool instead of thread-per-request
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((bind_ip, bind_port))
    print(f"Listening on {bind_ip}:{bind_port} with {MAX_WORKERS} workers...")
    
    while True:
        try:
            data, addr = s.recvfrom(4096)
            # Submit the query handling to the thread pool
            executor.submit(handle_query, data, addr, s)
        except Exception as e:
            print(f"Error in server loop: {e}")


if __name__ == "__main__":
    print("Starting custom DNS resolver (iterative) with caching:", ENABLE_CACHE)
    udp_server(bind_ip="0.0.0.0", bind_port=PORT)