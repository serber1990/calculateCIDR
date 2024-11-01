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
CYAN = "\033[0;36m"
MAGENTA = "\033[0;35m"

# Function to display help message
def show_help():
    print("Usage: {} -ip <IP/prefix> [-divide <N>] [-binary] [-vertical] [-v] [-h]".format(sys.argv[0]))
    print("Options:")
    print("  -ip <IP/prefix>: IP address with prefix (required)")
    print("  -divide <N>: Divide the network into N subnets (disables vertical display)")
    print("  -binary: Display results in binary format")
    print("  -vertical: Display results in vertical format (applies only without -divide)")
    print("  -v: Display version information")
    print("  -h: Display this help message")

# Function to convert IP address to binary format
def ip_to_binary(ip):
    return ".".join(f"{int(octet):08b}" for octet in ip.split("."))

# Function to calculate network details
def calculate_network(ip_prefix, binary=False):
    network = ipaddress.ip_network(ip_prefix, strict=False)
    netmask = str(network.netmask)
    network_id = str(network.network_address)
    gateway = str(list(network.hosts())[0]) if network.num_addresses > 2 else "N/A"
    broadcast = str(network.broadcast_address)
    hosts = network.num_addresses - 2 if network.num_addresses > 2 else 0
    
    if binary:
        netmask = ip_to_binary(netmask)
        network_id = ip_to_binary(network_id)
        gateway = ip_to_binary(gateway) if gateway != "N/A" else "N/A"
        broadcast = ip_to_binary(broadcast)
    
    return (netmask, network_id, gateway, broadcast, hosts)

# Function to calculate subnets
def calculate_subnets(ip_prefix, divide, binary=False):
    network = ipaddress.ip_network(ip_prefix, strict=False)
    subnets = list(network.subnets(new_prefix=network.prefixlen + (divide.bit_length() - 1)))
    subnet_data = []
    for i, subnet in enumerate(subnets[:divide]):
        network_id = str(subnet.network_address)
        gateway = str(list(subnet.hosts())[0]) if subnet.num_addresses > 2 else "N/A"
        broadcast = str(subnet.broadcast_address)
        netmask = str(subnet.netmask)
        hosts = subnet.num_addresses - 2 if subnet.num_addresses > 2 else 0
        
        if binary:
            network_id = ip_to_binary(network_id)
            gateway = ip_to_binary(gateway) if gateway != "N/A" else "N/A"
            broadcast = ip_to_binary(broadcast)
            netmask = ip_to_binary(netmask)
        
        subnet_data.append([
            f"{MAGENTA}{subnet}{RESET}", 
            f"{YELLOW}{network_id}{RESET}",
            f"{CYAN}{gateway}{RESET}",
            f"{RED}{broadcast}{RESET}", 
            f"{YELLOW}{netmask}{RESET}", 
            f"{MAGENTA}{hosts}{RESET}"
        ])
    return subnet_data

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-ip", help="IP address with prefix (required)")
parser.add_argument("-divide", type=int, help="Divide the network into N subnets (disables vertical display)")
parser.add_argument("-binary", action="store_true", help="Display results in binary format")
parser.add_argument("-vertical", action="store_true", help="Display results in vertical format (only without -divide)")
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

# Check if binary display is requested
binary = args.binary

# Calculate and display subnets if -divide option is provided
if args.divide:
    divide = args.divide
    subnet_data = calculate_subnets(ip_prefix, divide, binary)
    if not subnet_data:
        print(f"{RED}[x] Error:{RESET} Unable to divide {ip_prefix} into {divide} subnets.")
        sys.exit(1)
    
    # Display subnets in horizontal format (ignoring -vertical)
    table_data = [[
        f"{GREEN}Subnet{RESET}", 
        f"{GREEN}Network ID{RESET}", 
        f"{GREEN}Gateway{RESET}", 
        f"{GREEN}Broadcast{RESET}", 
        f"{GREEN}Netmask{RESET}", 
        f"{GREEN}Hosts{RESET}"
    ]] + subnet_data
    print(tabulate(table_data, headers="firstrow", tablefmt="grid", colalign=("left",)))

else:
    # Calculate main network details with Gateway column
    netmask, network_id, gateway, broadcast, hosts = calculate_network(ip_prefix, binary)

    # Create the table data in vertical format if -vertical option is specified
    if args.vertical:
        table_data = [
            [f"{GREEN}IP{RESET}", f"{MAGENTA}{ip_prefix}{RESET}"],
            [f"{GREEN}Network ID{RESET}", f"{YELLOW}{network_id}{RESET}"],
            [f"{GREEN}Gateway{RESET}", f"{CYAN}{gateway}{RESET}"],
            [f"{GREEN}Broadcast{RESET}", f"{RED}{broadcast}{RESET}"],
            [f"{GREEN}Netmask{RESET}", f"{YELLOW}{netmask}{RESET}"],
            [f"{GREEN}Hosts{RESET}", f"{MAGENTA}{hosts}{RESET}"]
        ]
        print(tabulate(table_data, tablefmt="grid"))
    else:
        # Display horizontally if -vertical is not specified
        table_data = [
            [f"{GREEN}IP{RESET}", f"{GREEN}Network ID{RESET}", f"{GREEN}Gateway{RESET}", f"{GREEN}Broadcast{RESET}", f"{GREEN}Netmask{RESET}", f"{GREEN}Hosts{RESET}"],
            [f"{MAGENTA}{ip_prefix}{RESET}", f"{YELLOW}{network_id}{RESET}", f"{CYAN}{gateway}{RESET}", f"{RED}{broadcast}{RESET}", f"{YELLOW}{netmask}{RESET}", f"{MAGENTA}{hosts}{RESET}"]
        ]
        print(tabulate(table_data, headers="firstrow", tablefmt="grid", colalign=("left",)))
