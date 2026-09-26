# Changelog

## 2.1.0

### Fixed
- `/31` networks reported 0 usable hosts; they now follow RFC 3021 (2 hosts, no broadcast). `/32` reports 1 host.
- The header box right border was misaligned.
- `tabulate` was declared as a dependency but no longer used.

### Added
- `--json` output for single networks and subnet divisions.
- Address type classification (Private RFC 1918, Public, CGNAT, Loopback, Link-local, Multicast, ULA, Documentation).
- Addresses with host bits (`10.1.2.3/20`) show the original address next to the network.
- The address can be passed positionally: `cidr 192.168.1.0/24` (`-ip` still works).
- Plain output when piped or when `NO_COLOR` is set; errors are written to stderr.
- Test suite and GitHub Actions CI.

### Changed
- "Gateway" is now labelled "First Host" (the first usable address is not always the gateway).
- `-vertical` is accepted but hidden (the layout is always vertical).
- Subnet generation is lazy, so large IPv6 divisions are instant.
- License file is now MIT, matching the package metadata. Requires Python 3.9+.

## 2.0.0

- IPv6, wildcard mask, division fix, clean UI, pip-installable.
