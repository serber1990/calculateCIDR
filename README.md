# calculateCIDR

[![CI](https://github.com/serber1990/calculateCIDR/actions/workflows/ci.yml/badge.svg)](https://github.com/serber1990/calculateCIDR/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/cidr-calculator.svg)](https://badge.fury.io/py/cidr-calculator)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/serber1990/calculateCIDR?style=social)](https://github.com/serber1990/calculateCIDR/stargazers)

Fast CIDR network calculator for the terminal: IPv4 & IPv6, subnet division, address classification,
binary view and JSON output for scripts.

<p align="center">
  <img src="https://raw.githubusercontent.com/serber1990/calculateCIDR/main/docs/demo.gif" alt="cidr demo: network details, subnet division and JSON output" width="820">
</p>

---

## ✨ Features

- 🌐 **IPv4 & IPv6** — network ID, host range, broadcast, netmask, wildcard and host count
- 🎯 **Any address works** — `10.1.2.3/20` shows the address *and* the network it belongs to
- 🧩 **Subnet division** — split any network into N subnets with correct prefix math
- 🏷️ **Address type** — Private (RFC 1918), Public, CGNAT, Loopback, Link-local, Multicast, Documentation…
- 📐 **RFC 3021 aware** — `/31` point-to-point links have 2 usable hosts, `/32` has 1
- 🔠 **Binary display** — every IPv4 field in binary octets
- 🤖 **JSON output** — pipe results into `jq`, Ansible or your own scripts
- 🔇 **Script-friendly** — plain output when piped or when `NO_COLOR` is set; errors go to stderr

---

## 📥 Installation

```bash
pip install cidr-calculator
```

Or from source:

```bash
git clone https://github.com/serber1990/calculateCIDR.git
cd calculateCIDR
pip install -e .
```

---

## 🛠 Usage

```bash
cidr IP/PREFIX [-divide N] [-binary] [--json]
```

| Option | Description |
|--------|-------------|
| `IP/PREFIX` | Address with CIDR prefix (`-ip IP/PREFIX` also works) |
| `-divide N` | Split the network into N subnets |
| `-binary` | Show IPv4 addresses in binary |
| `-j`, `--json` | Machine-readable JSON output |
| `-v`, `--version` | Show version |
| `-h`, `--help` | Show help |

---

## 🎨 Examples

### Network details

```bash
cidr 192.168.1.10/24
```

```
  ╔══════════════════════════════════════════════╗
  ║ 192.168.1.0/24  ·  IPv4                      ║
  ╚══════════════════════════════════════════════╝

  Address     192.168.1.10
  Network ID  192.168.1.0
  First Host  192.168.1.1
  Last Host   192.168.1.254
  Broadcast   192.168.1.255
  Netmask     255.255.255.0
  Wildcard    0.0.0.255
  Prefix      /24
  Hosts       254
  Type        Private (RFC 1918)
```

### Subnet division

```bash
cidr 192.168.1.0/24 -divide 4
```

```
  ╔════════════════════════════════════════════════════╗
  ║ 192.168.1.0/24  ·  4 subnets  /  new prefix /26    ║
  ╚════════════════════════════════════════════════════╝

  #  Subnet            Network ID     First Host     Last Host      Broadcast      Netmask          Wildcard  Hosts
  ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  1  192.168.1.0/26    192.168.1.0    192.168.1.1    192.168.1.62   192.168.1.63   255.255.255.192  0.0.0.63  62
  2  192.168.1.64/26   192.168.1.64   192.168.1.65   192.168.1.126  192.168.1.127  255.255.255.192  0.0.0.63  62
  3  192.168.1.128/26  192.168.1.128  192.168.1.129  192.168.1.190  192.168.1.191  255.255.255.192  0.0.0.63  62
  4  192.168.1.192/26  192.168.1.192  192.168.1.193  192.168.1.254  192.168.1.255  255.255.255.192  0.0.0.63  62
```

When N is not a power of two, the next power is used and the first N subnets are shown.

### JSON for scripts

```bash
cidr 10.0.0.0/30 --json
```

```json
{
  "input": "10.0.0.0/30",
  "address": "10.0.0.0",
  "network": "10.0.0.0/30",
  "version": 4,
  "network_id": "10.0.0.0",
  "broadcast": "10.0.0.3",
  "netmask": "255.255.255.252",
  "wildcard": "0.0.0.3",
  "prefix": 30,
  "first_host": "10.0.0.1",
  "last_host": "10.0.0.2",
  "usable_hosts": 2,
  "total_addresses": 4,
  "type": "Private (RFC 1918)"
}
```

```bash
# Usable hosts of a network, straight into a variable
hosts=$(cidr 10.20.0.0/22 --json | jq .usable_hosts)
```

### Binary and IPv6

```bash
cidr 192.168.1.0/24 -binary
cidr 2001:db8::/32 -divide 16
```

---

## 🧪 Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

See [CHANGELOG.md](CHANGELOG.md) for release notes.

---

## 📝 License

MIT — see [LICENSE](LICENSE).

---

## 💬 Feedback

Open an issue or reach out via GitHub.

## 🌐 Connect

[![GitHub](https://img.shields.io/badge/GitHub-@serber1990-181717?style=flat-square&logo=github)](https://github.com/serber1990)
