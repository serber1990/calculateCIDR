# calculateCIDR

calculateCIDR is a Python command-line tool for calculating CIDR network details, with the ability to split networks into subnets, display results in binary format, and output details in either horizontal or vertical format. The tool also leverages ANSI colors to improve readability.

---

## ✨ Features

- 🔢 **CIDR Calculation**: Calculates network ID, gateway, broadcast address, netmask, and host count from any CIDR notation.
- 🧩 **Subnet Division**: Divides a CIDR block into multiple subnets with calculated properties for each.
- 🔠 **Binary Display Option**: Displays IPs and subnet masks in binary format for better visualization.
- 📏 **Flexible Formatting**: Outputs data in horizontal or vertical formats.
- 🌈 **ANSI Colors**: Uses the `colorize-term` library for colorful terminal output, improving readability.

---

## 📥 Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/serber1990/calculateCIDR.git
cd calculateCIDR
pip install -r requirements.txt
```

Install `colorize-term` for colorful output:
```bash
pip install colorize-term
```

---

## 🛠 Usage

```bash
python calculateCIDR.py -ip <IP/prefix> [-divide <N>] [-binary] [-vertical] [-v] [-h]
```

### Options

- `-ip <IP/prefix>`: IP address with CIDR prefix (required).
- `-divide <N>`: Divides the network into `N` subnets (disables vertical display).
- `-binary`: Displays results in binary format.
- `-vertical`: Displays results in vertical format (only applicable without `-divide`).
- `-v`: Shows version information.
- `-h`: Displays the help message.

---

## 🎨 Examples

### Basic CIDR Calculation

```bash
python calculateCIDR.py -ip 192.168.1.0/24
```

This command outputs the network ID, gateway, broadcast address, netmask, and host count for the specified CIDR.

### Binary Format

```bash
python calculateCIDR.py -ip 192.168.1.0/24 -binary
```

Displays the results in binary format.

### Subnet Division

```bash
python calculateCIDR.py -ip 192.168.1.0/24 -divide 4
```

Divides the network into 4 subnets, displaying each subnet’s details.

### Vertical Format

```bash
python calculateCIDR.py -ip 192.168.1.0/24 -vertical
```

Displays the network information in vertical format.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Feedback

If you have any questions, issues, or suggestions, please feel free to open an issue in the repository or contact me directly via GitHub.

---

## 🌐 Connect with Me

[![GitHub](https://img.shields.io/badge/GitHub-@serber1990-181717?style=flat-square&logo=github)](https://github.com/serber1990)

---

### 🚀 Let's make CIDR calculations easy and colorful with `calculateCIDR`!
