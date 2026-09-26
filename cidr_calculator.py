#!/usr/bin/env python3
"""
cidr — CIDR network calculator for IPv4 and IPv6.
Network details, subnet division, binary display and JSON output.
"""
import argparse
import ipaddress
import json
import math
import os
import re
import sys
from itertools import islice
from typing import Dict, List, Tuple, Union

from shellcolorize import Color

VERSION = "2.1.0"

Network = Union[ipaddress.IPv4Network, ipaddress.IPv6Network]

# ── ANSI helpers ──────────────────────────────────────────────────────────────

_ANSI = re.compile(r'\033\[[0-9;]*m')


def _vlen(s: str) -> int:
    """Visible length of a string (strips ANSI codes)."""
    return len(_ANSI.sub('', s))


def _pad(s: str, width: int) -> str:
    """Right-pad a string to a visible width."""
    return s + ' ' * max(0, width - _vlen(s))

# ── Display helpers ───────────────────────────────────────────────────────────

def _header(line1: str, line2: str = '') -> None:
    inner = f' {line1}'
    if line2:
        inner += f'  {Color.DIM}·{Color.RESET}  {line2}'
    w = max(46, _vlen(inner) + 4)
    print()
    print(f"  {Color.CYAN}╔{'═' * w}╗{Color.RESET}")
    print(f"  {Color.CYAN}║{Color.RESET}{Color.BOLD}{inner}{Color.RESET}"
          + ' ' * max(0, w - _vlen(inner))
          + f"{Color.CYAN}║{Color.RESET}")
    print(f"  {Color.CYAN}╚{'═' * w}╝{Color.RESET}")
    print()


def _separator(width: int = 72) -> None:
    print(f"  {Color.DIM}{'─' * width}{Color.RESET}")

# ── Network math ──────────────────────────────────────────────────────────────

def ip_to_binary(ip: str) -> str:
    """Dotted binary notation for an IPv4 address: 192.168.1.0 → 11000000.10101000.…"""
    return '.'.join(f'{int(o):08b}' for o in ip.split('.'))


def host_range(net: Network) -> Tuple[str, str, int]:
    """
    First usable host, last usable host and number of usable hosts.

    IPv4 reserves the network and broadcast addresses, except for point-to-point
    /31 links (RFC 3021) and single-host /32 routes. IPv6 has no broadcast, so
    every address is usable.
    """
    total = net.num_addresses
    if net.version == 4 and total > 2:
        return str(net.network_address + 1), str(net.broadcast_address - 1), total - 2
    return str(net.network_address), str(net.broadcast_address), total


_DOCUMENTATION = [ipaddress.ip_network(n) for n in
                  ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24', '2001:db8::/32')]


def broadcast(net: Network):
    """Broadcast address, or None for IPv6 and IPv4 /31–/32 (no broadcast there)."""
    if net.version == 4 and net.prefixlen < 31:
        return str(net.broadcast_address)
    return None


def address_type(net: Network) -> str:
    """Human-readable classification of the address block."""
    if any(net.version == d.version and net.subnet_of(d) for d in _DOCUMENTATION):
        return 'Documentation'
    if net.is_loopback:
        return 'Loopback'
    if net.is_link_local:
        return 'Link-local'
    if net.is_multicast:
        return 'Multicast'
    if net.version == 4 and net.subnet_of(ipaddress.ip_network('100.64.0.0/10')):
        return 'Shared / CGNAT (RFC 6598)'
    if net.version == 6 and net.subnet_of(ipaddress.ip_network('fc00::/7')):
        return 'Unique local (RFC 4193)'
    if net.version == 4 and any(net.subnet_of(ipaddress.ip_network(b))
                                for b in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')):
        return 'Private (RFC 1918)'
    if net.is_global:
        return 'Public'
    if net.is_private:
        return 'Private / special-purpose'
    return 'Reserved'


def calculate_network(address: str) -> Dict:
    """Details for the network containing `address` (e.g. '192.168.1.10/24')."""
    iface = ipaddress.ip_interface(address.strip())
    net = iface.network
    first, last, hosts = host_range(net)
    return {
        'input': str(iface),
        'address': str(iface.ip),
        'network': str(net),
        'version': net.version,
        'network_id': str(net.network_address),
        'broadcast': broadcast(net),
        'netmask': str(net.netmask),
        'wildcard': str(net.hostmask),
        'prefix': net.prefixlen,
        'first_host': first,
        'last_host': last,
        'usable_hosts': hosts,
        'total_addresses': net.num_addresses,
        'type': address_type(net),
    }


def subnet_prefix(net: Network, count: int) -> int:
    """Smallest prefix that splits `net` into at least `count` subnets."""
    if count < 1:
        raise ValueError('count must be a positive integer')
    return net.prefixlen + math.ceil(math.log2(count))


def calculate_subnets(network: str, count: int) -> Tuple[List[Dict], int]:
    """
    Split `network` into `count` subnets. Returns (subnets, new_prefix).
    When `count` is not a power of two the next power is used and the first
    `count` subnets are returned. Raises ValueError if the prefix would overflow.
    """
    net = ipaddress.ip_network(network.strip(), strict=False)
    new_pfx = subnet_prefix(net, count)
    if new_pfx > net.max_prefixlen:
        raise ValueError(f'cannot divide {net} into {count} subnets — '
                         f'prefix would exceed /{net.max_prefixlen}')
    rows = []
    for subnet in islice(net.subnets(new_prefix=new_pfx), count):
        first, last, hosts = host_range(subnet)
        rows.append({
            'subnet': str(subnet),
            'network_id': str(subnet.network_address),
            'first_host': first,
            'last_host': last,
            'broadcast': broadcast(subnet),
            'netmask': str(subnet.netmask),
            'wildcard': str(subnet.hostmask),
            'usable_hosts': hosts,
        })
    return rows, new_pfx

# ── Output ────────────────────────────────────────────────────────────────────

_IP_FIELDS = ('address', 'network_id', 'first_host', 'last_host', 'broadcast', 'netmask', 'wildcard')


def _as_binary(info: Dict) -> Dict:
    """Copy of `info` with every IPv4 address field in binary notation."""
    if ':' in info['network_id']:   # binary notation only makes sense for IPv4
        return info
    return {k: (ip_to_binary(v) if k in _IP_FIELDS and v else v) for k, v in info.items()}


def print_network(info: Dict, binary: bool = False) -> None:
    shown = _as_binary(info) if binary else info
    _header(info['network'], f"IPv{info['version']}")

    fields = []
    if info['address'] != info['network_id']:
        fields.append(('Address', Color.BOLD, shown['address']))
    fields += [
        ('Network ID', Color.YELLOW, shown['network_id']),
        ('First Host', Color.CYAN,   shown['first_host']),
        ('Last Host',  Color.CYAN,   shown['last_host']),
    ]
    if shown['broadcast']:
        fields.append(('Broadcast', Color.RED, shown['broadcast']))
    fields += [
        ('Netmask',  '',            shown['netmask']),
        ('Wildcard', Color.MAGENTA, shown['wildcard']),
        ('Prefix',   '',            f"/{info['prefix']}"),
        ('Hosts',    Color.YELLOW + Color.BOLD, f"{info['usable_hosts']:,}"),
        ('Type',     Color.DIM,     info['type']),
    ]

    lw = max(len(f[0]) for f in fields)
    for label, color, value in fields:
        val = f"{color}{value}{Color.RESET}" if color else value
        print(f"  {Color.GREEN}{label:<{lw}}{Color.RESET}  {val}")
    print()


def print_subnets(rows: List[Dict], network: str, count: int, new_pfx: int,
                  binary: bool = False) -> None:
    total = 2 ** (new_pfx - ipaddress.ip_network(network, strict=False).prefixlen)
    extra = f'  (first {count} of {total})' if count != total else ''
    _header(network, f'{count} subnets  /  new prefix /{new_pfx}{extra}')

    is_v4 = rows[0]['broadcast'] is not None
    cols = [('#', ''), ('Subnet', Color.YELLOW), ('Network ID', Color.YELLOW),
            ('First Host', Color.CYAN), ('Last Host', Color.CYAN)]
    if is_v4:
        cols.append(('Broadcast', Color.RED))
    cols += [('Netmask', ''), ('Wildcard', Color.MAGENTA), ('Hosts', Color.YELLOW + Color.BOLD)]

    data = []
    for i, r in enumerate(rows, 1):
        s = _as_binary(r) if binary else r
        row = [str(i), r['subnet'], s['network_id'], s['first_host'], s['last_host']]
        if is_v4:
            row.append(s['broadcast'])
        row += [s['netmask'], s['wildcard'], f"{r['usable_hosts']:,}"]
        data.append(row)

    widths = [max(len(name), *(len(row[j]) for row in data)) for j, (name, _) in enumerate(cols)]
    print('  ' + '  '.join(f"{Color.GREEN}{Color.BOLD}{name:<{w}}{Color.RESET}"
                           for (name, _), w in zip(cols, widths)))
    _separator(sum(widths) + 2 * (len(widths) - 1))
    for row in data:
        cells = [_pad(f"{color}{value}{Color.RESET}" if color else value, w)
                 for value, (_, color), w in zip(row, cols, widths)]
        print('  ' + '  '.join(cells))
    print()

# ── CLI ───────────────────────────────────────────────────────────────────────

def _error(msg: str) -> None:
    print(f'\n  {Color.RED}✖  Error:{Color.RESET} {msg}\n', file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='cidr',
        description='CIDR network calculator — IPv4 & IPv6',
        epilog='examples:  cidr 192.168.1.0/24   ·   cidr 10.0.0.0/8 -divide 4   ·   cidr 2001:db8::/32 --json',
    )
    parser.add_argument('address', nargs='?', metavar='IP/PREFIX',
                        help='IP address with CIDR prefix (e.g. 192.168.1.10/24 or 2001:db8::/32)')
    parser.add_argument('-ip', '--ip', dest='ip', metavar='IP/PREFIX',
                        help='Same as the positional argument (kept for backward compatibility)')
    parser.add_argument('-divide', '--divide', type=int, metavar='N',
                        help='Divide the network into N subnets')
    parser.add_argument('-binary', '--binary', action='store_true',
                        help='Display IPv4 addresses in binary')
    parser.add_argument('-j', '--json', action='store_true',
                        help='Machine-readable JSON output')
    parser.add_argument('-vertical', '--vertical', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='version', version=f'cidr {VERSION}')
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    Color.auto()

    address = args.address or args.ip
    if not address:
        parser.print_help()
        sys.exit(0)

    try:
        info = calculate_network(address)
    except ValueError as e:
        _error(str(e))
        sys.exit(1)

    if args.divide is not None:
        if args.divide < 1:
            _error('-divide must be a positive integer.')
            sys.exit(1)
        try:
            rows, new_pfx = calculate_subnets(info['network'], args.divide)
        except ValueError as e:
            _error(str(e))
            sys.exit(1)
        if args.json:
            print(json.dumps({'network': info['network'], 'new_prefix': new_pfx,
                              'subnets': rows}, indent=2))
        else:
            print_subnets(rows, info['network'], args.divide, new_pfx, args.binary)
    elif args.json:
        print(json.dumps(info, indent=2))
    else:
        print_network(info, args.binary)


def run() -> None:
    """Console entry point: like main(), but quiet when the output pipe is closed early (| head)."""
    try:
        main()
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(141)


if __name__ == '__main__':
    run()
