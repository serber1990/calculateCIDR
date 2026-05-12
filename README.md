# calculateCIDR

[![PyPI version](https://badge.fury.io/py/cidr-calculator.svg)](https://badge.fury.io/py/cidr-calculator)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/serber1990/calculateCIDR?style=social)](https://github.com/serber1990/calculateCIDR/stargazers)

CLI CIDR network calculator with IPv4 & IPv6 support, wildcard mask, subnet division and binary display.

---

## ✨ Features

- 🌐 **IPv4 & IPv6** — full support for both address families
- 🧩 **Subnet division** — split any network into N subnets with correct prefix math
- 🔢 **Wildcard mask** — inverse netmask (Cisco-style) included in every output
- 🔠 **Binary display** — view any field in binary octet notation (IPv4)
- 📏 **Flexible output** — horizontal (default) or vertical format
- 🌈 **Color-coded** — ANSI colors for fast readability

---

## 📥 Installation

```bash
pip install cidr-calculator
```

Or clone and install locally:

```bash
git clone https://github.com/serber1990/calculateCIDR.git
cd calculateCIDR
pip install -e .
```

---

## 🛠 Usage

```bash
cidr -ip <IP/PREFIX> [-divide N] [-binary] [-vertical] [-v] [-h]
```

| Flag | Description |
|------|-------------|
| `-ip IP/PREFIX` | IP address with CIDR prefix — **required** |
| `-divide N` | Split the network into N subnets |
| `-binary` | Display results in binary (IPv4 only) |
| `-vertical` | Vertical output format (without `-divide`) |
| `-v` | Show version |
| `-h` | Show help |

---

## 🎨 Examples

### Basic calculation

```bash
cidr -ip 192.168.1.0/24
```

```
+-----------------+-------------+-----------+-----------+-----------------+---------------+---------------+---------+
| Network         | Network ID  | Gateway   | Last Host | Broadcast       | Netmask       | Wildcard      | Hosts   |
+=================+=============+===========+===========+=================+===============+===============+=========+
| 192.168.1.0/24  | 192.168.1.0 | 192.168.1.1 | 192.168.1.254 | 192.168.1.255 | 255.255.255.0 | 0.0.0.255 | 254 |
+-----------------+-------------+-----------+-----------+-----------------+---------------+---------------+---------+
```

### Vertical format

```bash
cidr -ip 10.0.0.0/8 -vertical
```

### Subnet division

```bash
cidr -ip 192.168.1.0/24 -divide 4
```

Splits `/24` into 4 subnets (`/26`), showing network ID, gateway, last host, broadcast, netmask, wildcard and host count for each.

### Binary display

```bash
cidr -ip 192.168.1.0/24 -binary
```

### IPv6

```bash
cidr -ip 2001:db8::/32
```

---

## 📝 License

MIT — see [LICENSE](LICENSE).

---

## 💬 Feedback

Open an issue or reach out via GitHub.

## 🌐 Connect

[![GitHub](https://img.shields.io/badge/GitHub-@serber1990-181717?style=flat-square&logo=github)](https://github.com/serber1990)
