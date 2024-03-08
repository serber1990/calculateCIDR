#!/usr/bin/env python3

import ipaddress
from tabulate import tabulate

def calculate_network_info(ip, cidr):
    ip_obj = ipaddress.ip_interface(f"{ip}/{cidr}")
    netmask = ip_obj.netmask
    network_id = ipaddress.ip_interface(ip_obj.network.network_address)
    broadcast_id = ipaddress.ip_interface(ip_obj.network.broadcast_address)
    total_hosts = 2 ** (32 - int(cidr))

    return netmask, network_id.ip, broadcast_id.ip, total_hosts

def colorize(text, color):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"

def main():
    while True:
        ip_cidr = input(colorize("Enter IP address with CIDR (e.g., 192.168.1.10/24), or 'q' to quit: ", "blue"))
        if ip_cidr.lower() == 'q':
            break
        
        try:
            ip, cidr = ip_cidr.split('/')
            ip_obj = ipaddress.ip_interface(f"{ip}/{cidr}")
        except ValueError:
            print("\n" + colorize("Invalid input. Please provide a valid IP address with CIDR notation.", "red") + "\n")
            continue
        
        netmask, network_id, broadcast_id, total_hosts = calculate_network_info(ip, cidr)

        table_data = [
            [colorize("Netmask", "cyan"), colorize(netmask, "red")],
            [colorize("Network ID", "cyan"), colorize(network_id, "red")],
            [colorize("Broadcast ID", "cyan"), colorize(broadcast_id, "red")],
            [colorize("Total Hosts", "cyan"), colorize(str(total_hosts), "red")]
        ]

        headers = ["Attribute", "Value"]
        print("\nInformation for IP/CIDR:", colorize(ip_cidr, "blue"))
        print("-" * 40)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        break  # Exit the loop if input is valid

if __name__ == "__main__":
    main()

