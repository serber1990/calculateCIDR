#!/usr/bin/env python3
import argparse
import ipaddress
import math
import re
import sys
from shellcolorize import Color

VERSION = "2.0.0"

# ── ANSI helpers ──────────────────────────────────────────────────────────────

_ANSI = re.compile(r'\033\[[0-9;]*m')

def _vlen(s: str) -> int:
    """Visible length of a string (strips ANSI codes)."""
    return len(_ANSI.sub('', s))

def _pad(s: str, width: int) -> str:
    """Left-pad a string to visible width."""
    return s + ' ' * max(0, width - _vlen(s))

# ── Display helpers ───────────────────────────────────────────────────────────

def _header(line1: str, line2: str = '') -> None:
    inner = f' {line1}'
    if line2:
        inner += f'  {Color.DIM}·{Color.RESET}  {line2}'
    w = max(46, _vlen(inner) + 4)
    border = f"{Color.CYAN}{'═' * w}{Color.RESET}"
    print()
    print(f"  {Color.CYAN}╔{border}╗{Color.RESET}")
    print(f"  {Color.CYAN}║{Color.RESET}{Color.BOLD}{inner}{Color.RESET}"
          + ' ' * max(0, w - _vlen(inner))
          + f"  {Color.CYAN}║{Color.RESET}")
    print(f"  {Color.CYAN}╚{border}╝{Color.RESET}")
    print()

def _row(label: str, value: str, label_w: int, value_color: str = '') -> None:
    lbl = f"  {Color.GREEN}{label:<{label_w}}{Color.RESET}  "
    val = f"{value_color}{value}{Color.RESET}" if value_color else value
    print(lbl + val)

def _separator(width: int = 72) -> None:
    print(f"  {Color.DIM}{'─' * width}{Color.RESET}")

# ── Network math ──────────────────────────────────────────────────────────────

def ip_to_binary(ip: str) -> str:
    return '.'.join(f'{int(o):08b}' for o in ip.split('.'))


def _first_last(network: ipaddress._BaseNetwork):
    if network.num_addresses <= 2:
        return 'N/A', 'N/A'
    return str(network.network_address + 1), str(network.broadcast_address - 1)


def calculate_network(ip_prefix: str, binary: bool = False) -> dict:
    net = ipaddress.ip_network(ip_prefix, strict=False)
    is_v6 = net.version == 6

    nid       = str(net.network_address)
    broadcast = str(net.broadcast_address) if not is_v6 else 'N/A'
    netmask   = str(net.netmask)
    wildcard  = str(net.hostmask)
    gateway, last_host = _first_last(net)
    total = net.num_addresses
    hosts = max(0, total - 2) if not is_v6 else total

    if binary and not is_v6:
        nid       = ip_to_binary(nid)
        broadcast = ip_to_binary(broadcast)
        netmask   = ip_to_binary(netmask)
        wildcard  = ip_to_binary(wildcard)
        if gateway   != 'N/A': gateway   = ip_to_binary(gateway)
        if last_host != 'N/A': last_host = ip_to_binary(last_host)

    return {
        'network': str(net), 'network_id': nid,
        'gateway': gateway, 'last_host': last_host,
        'broadcast': broadcast, 'netmask': netmask,
        'wildcard': wildcard, 'prefix': net.prefixlen,
        'hosts': hosts, 'is_v6': is_v6,
    }


def calculate_subnets(ip_prefix: str, divide: int, binary: bool = False):
    net = ipaddress.ip_network(ip_prefix, strict=False)
    is_v6 = net.version == 6
    max_pfx = 128 if is_v6 else 32

    bits = math.ceil(math.log2(divide)) if divide > 1 else 0
    new_pfx = net.prefixlen + bits
    if new_pfx > max_pfx:
        return [], new_pfx

    rows = []
    for subnet in list(net.subnets(new_prefix=new_pfx))[:divide]:
        nid      = str(subnet.network_address)
        bc       = str(subnet.broadcast_address) if not is_v6 else 'N/A'
        nm       = str(subnet.netmask)
        wc       = str(subnet.hostmask)
        gw, last = _first_last(subnet)
        total    = subnet.num_addresses
        hosts    = max(0, total - 2) if not is_v6 else total

        if binary and not is_v6:
            nid  = ip_to_binary(nid)
            bc   = ip_to_binary(bc)
            nm   = ip_to_binary(nm)
            wc   = ip_to_binary(wc)
            if gw   != 'N/A': gw   = ip_to_binary(gw)
            if last != 'N/A': last = ip_to_binary(last)

        rows.append({
            'subnet': str(subnet), 'network_id': nid,
            'gateway': gw, 'last_host': last,
            'broadcast': bc, 'netmask': nm,
            'wildcard': wc, 'hosts': hosts,
        })
    return rows, new_pfx

# ── Output ────────────────────────────────────────────────────────────────────

def print_network(info: dict) -> None:
    version = 'IPv6' if info['is_v6'] else 'IPv4'
    _header(info['network'], version)

    fields = [
        ('Network ID', Color.YELLOW,  info['network_id']),
        ('Gateway',    Color.CYAN,    info['gateway']),
        ('Last Host',  Color.CYAN,    info['last_host']),
    ]
    if not info['is_v6']:
        fields.append(('Broadcast', Color.RED, info['broadcast']))
    fields += [
        ('Netmask',  '',             info['netmask']),
        ('Wildcard', Color.MAGENTA,  info['wildcard']),
        ('Prefix',   '',             f"/{info['prefix']}"),
        ('Hosts',    Color.YELLOW + Color.BOLD, f"{info['hosts']:,}"),
    ]

    lw = max(len(f[0]) for f in fields)
    for label, color, value in fields:
        _row(label, value, lw, color)
    print()


def print_subnets(rows: list, ip_prefix: str, divide: int, new_pfx: int) -> None:
    _header(f'{ip_prefix}', f'{divide} subnets  /  new prefix  /{new_pfx}')

    cols = ['#', 'Subnet', 'Network ID', 'Gateway', 'Last Host',
            'Broadcast', 'Netmask', 'Wildcard', 'Hosts']

    # Build raw (no color) data for width calculation
    raw = []
    for i, r in enumerate(rows):
        raw.append([
            str(i + 1), r['subnet'], r['network_id'], r['gateway'],
            r['last_host'], r['broadcast'], r['netmask'], r['wildcard'],
            f"{r['hosts']:,}",
        ])

    # Column widths = max of header vs data
    widths = [max(len(cols[j]), max((len(raw[i][j]) for i in range(len(raw))), default=0))
              for j in range(len(cols))]

    # Header row
    header_cells = [
        f"{Color.GREEN}{Color.BOLD}{cols[j]:<{widths[j]}}{Color.RESET}"
        for j in range(len(cols))
    ]
    print('  ' + '  '.join(header_cells))
    _separator(sum(widths) + 2 * (len(widths) - 1))

    # Value colors per column
    value_colors = [
        '',             # #
        Color.YELLOW,   # Subnet
        Color.YELLOW,   # Network ID
        Color.CYAN,     # Gateway
        Color.CYAN,     # Last Host
        Color.RED,      # Broadcast
        '',             # Netmask
        Color.MAGENTA,  # Wildcard
        Color.YELLOW + Color.BOLD,  # Hosts
    ]

    for i, r in enumerate(raw):
        cells = [
            _pad(f"{value_colors[j]}{r[j]}{Color.RESET}" if value_colors[j] else r[j], widths[j])
            for j in range(len(cols))
        ]
        print('  ' + '  '.join(cells))
    print()

# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='cidr',
        description='CIDR network calculator — IPv4 & IPv6',
        add_help=False,
    )
    parser.add_argument('-ip', '--ip', metavar='IP/PREFIX',
                        help='IP address with CIDR prefix  (e.g. 192.168.1.0/24 or 2001:db8::/32)')
    parser.add_argument('-divide', '--divide', type=int, metavar='N',
                        help='Divide the network into N subnets')
    parser.add_argument('-binary', '--binary', action='store_true',
                        help='Display IPs in binary format (IPv4 only)')
    parser.add_argument('-vertical', '--vertical', action='store_true',
                        help='Kept for backward compatibility (layout is always clean)')
    parser.add_argument('-v', '--version', action='store_true', help='Show version and exit')
    parser.add_argument('-h', '--help',    action='store_true', help='Show this help and exit')
    args = parser.parse_args()

    if args.version:
        print(f'cidr v{VERSION}')
        sys.exit(0)

    if args.help or args.ip is None:
        parser.print_help()
        sys.exit(0)

    try:
        net = ipaddress.ip_network(args.ip.strip(), strict=False)
    except ValueError as e:
        print(f'\n  {Color.RED}✖  Error:{Color.RESET} {e}\n')
        sys.exit(1)

    ip_prefix = str(net)

    if args.divide:
        if args.divide < 1:
            print(f'\n  {Color.RED}✖  Error:{Color.RESET} -divide must be a positive integer.\n')
            sys.exit(1)
        rows, new_pfx = calculate_subnets(ip_prefix, args.divide, args.binary)
        if not rows:
            max_p = 128 if net.version == 6 else 32
            print(f'\n  {Color.RED}✖  Error:{Color.RESET} Cannot divide {ip_prefix} into '
                  f'{args.divide} subnets — prefix would exceed /{max_p}.\n')
            sys.exit(1)
        print_subnets(rows, ip_prefix, args.divide, new_pfx)
    else:
        info = calculate_network(ip_prefix, args.binary)
        print_network(info)


if __name__ == '__main__':
    main()
