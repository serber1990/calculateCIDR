#!/usr/bin/env python3

import argparse
import ipaddress
import sys
from tabulate import tabulate

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Function to display help message
def show_help():
    print("Usage: {} -ip <IP/prefix> [-divide <N>] [-v] [-h]".format(sys.argv[0]))
    print("Options:")
    print("  -ip <IP/prefix>: IP address with prefix (required)")
    print("  -divide <N>: Divide the network into N subnets")
    print("  -v: Display version information")
    print("  -h: Display this help message")

# Function to calculate network details
def calculate_network(ip_prefix):
    network = ipaddress.ip_network(ip_prefix, strict=False)
    netmask = str(network.netmask)
    network_id = str(network.network_address)
    broadcast = str(network.broadcast_address)
    hosts = network.num_addresses - 2
    return (netmask, network_id, broadcast, hosts)

# Function to calculate subnets
def calculate_subnets(ip_prefix, divide):
    network = ipaddress.ip_network(ip_prefix, strict=False)
    subnets = list(network.subnets(new_prefix=network.prefixlen + (divide.bit_length() - 1)))
    subnet_data = []
    for i, subnet in enumerate(subnets[:divide]):
        gateway = str(list(subnet.hosts())[0]) if subnet.num_addresses > 2 else "N/A"
        broadcast = str(subnet.broadcast_address)
        hosts = subnet.num_addresses - 2 if subnet.num_addresses > 2 else 0
        subnet_data.append([
            f"{YELLOW}{subnet}{RESET}", 
            f"{YELLOW}{subnet.netmask}{RESET}", 
            f"{YELLOW}{subnet.network_address}{RESET}", 
            f"{YELLOW}{broadcast}{RESET}", 
            f"{YELLOW}{hosts}{RESET}", 
            f"{YELLOW}{gateway}{RESET}"
        ])
    return subnet_data

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-ip", help="IP address with prefix (required)")
parser.add_argument("-divide", type=int, help="Divide the network into N subnets")
parser.add_argument("-v", action="store_true", help="Display version information")
args = parser.parse_args()

# Display version information
if args.v:
    print("Version 1.0 by Serber")
    sys.exit(0)

# Display help message if no arguments provided
if len(sys.argv) == 1:
    show_help()
    sys.exit(0)

# Display help message if -h option provided
if args.ip is None:
    show_help()
    sys.exit(0)

# Prompt user to input IP/prefix
ip_prefix = args.ip.strip().upper()

# Check if the IP has a prefix
if '/' not in ip_prefix:
    print(f"{RED}[x] Error:{RESET} The IP does not have a prefix.")
    print(f"[!] Insert a valid IP with a prefix p.e: {GREEN}10.10.10.10/24{RESET}")
    sys.exit(1)

# Calculate and display subnets if -divide option is provided
if args.divide:
    divide = args.divide
    subnet_data = calculate_subnets(ip_prefix, divide)
    if not subnet_data:
        print(f"{RED}[x] Error:{RESET} Unable to divide {ip_prefix} into {divide} subnets.")
        sys.exit(1)
    
    # Create the table data for subnets
    table_data = [[
        f"{GREEN}Subnet{RESET}", 
        f"{GREEN}Netmask{RESET}", 
        f"{GREEN}Network ID{RESET}", 
        f"{GREEN}Broadcast{RESET}", 
        f"{GREEN}Hosts{RESET}", 
        f"{GREEN}Gateway{RESET}"
    ]] + subnet_data
    print(tabulate(table_data, headers="firstrow", tablefmt="grid", colalign=("left",)))
else:
    # Calculate main network details
    netmask, network_id, broadcast, hosts = calculate_network(ip_prefix)
    table_data = [
        [f"{GREEN}IP{RESET}", f"{GREEN}Netmask{RESET}", f"{GREEN}Network ID{RESET}", f"{GREEN}Broadcast{RESET}", f"{GREEN}Hosts{RESET}"],
        [f"{YELLOW}{ip_prefix}{RESET}", f"{YELLOW}{netmask}{RESET}", f"{YELLOW}{network_id}{RESET}", f"{YELLOW}{broadcast}{RESET}", f"{YELLOW}{hosts}{RESET}"]
    ]
    print(tabulate(table_data, headers="firstrow", tablefmt="grid", colalign=("left",)))
