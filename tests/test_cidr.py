import json

import pytest

import cidr_calculator as cidr


def test_basic_ipv4():
    info = cidr.calculate_network("192.168.1.0/24")
    assert info["network_id"] == "192.168.1.0"
    assert info["first_host"] == "192.168.1.1"
    assert info["last_host"] == "192.168.1.254"
    assert info["broadcast"] == "192.168.1.255"
    assert info["netmask"] == "255.255.255.0"
    assert info["wildcard"] == "0.0.0.255"
    assert info["usable_hosts"] == 254
    assert info["total_addresses"] == 256
    assert info["type"] == "Private (RFC 1918)"


def test_host_bits_are_kept_as_address():
    info = cidr.calculate_network("10.1.2.3/20")
    assert info["network"] == "10.1.0.0/20"
    assert info["address"] == "10.1.2.3"


def test_no_prefix_means_single_host():
    info = cidr.calculate_network("8.8.8.8")
    assert info["prefix"] == 32
    assert info["usable_hosts"] == 1
    assert info["type"] == "Public"


def test_rfc3021_point_to_point():
    info = cidr.calculate_network("10.0.0.0/31")
    assert (info["first_host"], info["last_host"], info["usable_hosts"]) == ("10.0.0.0", "10.0.0.1", 2)
    assert info["broadcast"] is None


def test_ipv6():
    info = cidr.calculate_network("2001:db8::/126")
    assert info["version"] == 6
    assert info["broadcast"] is None
    assert info["usable_hosts"] == 4
    assert info["last_host"] == "2001:db8::3"
    assert info["type"] == "Documentation"


@pytest.mark.parametrize("net, kind", [
    ("127.0.0.1/8", "Loopback"),
    ("169.254.0.0/16", "Link-local"),
    ("224.0.0.0/4", "Multicast"),
    ("100.64.0.0/10", "Shared / CGNAT (RFC 6598)"),
    ("172.20.0.0/16", "Private (RFC 1918)"),
    ("fd00::/8", "Unique local (RFC 4193)"),
    ("1.1.1.0/24", "Public"),
])
def test_address_type(net, kind):
    assert cidr.calculate_network(net)["type"] == kind


def test_invalid_input():
    with pytest.raises(ValueError):
        cidr.calculate_network("300.1.1.1/24")
    with pytest.raises(ValueError):
        cidr.calculate_network("10.0.0.0/33")


def test_subnets_power_of_two():
    rows, pfx = cidr.calculate_subnets("192.168.1.0/24", 4)
    assert pfx == 26
    assert [r["subnet"] for r in rows] == [
        "192.168.1.0/26", "192.168.1.64/26", "192.168.1.128/26", "192.168.1.192/26"]
    assert all(r["usable_hosts"] == 62 for r in rows)


def test_subnets_round_up_and_truncate():
    rows, pfx = cidr.calculate_subnets("10.0.0.0/8", 3)
    assert pfx == 10
    assert len(rows) == 3


def test_subnets_overflow():
    with pytest.raises(ValueError, match="exceed /32"):
        cidr.calculate_subnets("10.0.0.0/30", 64)


def test_huge_ipv6_division_is_lazy():
    rows, pfx = cidr.calculate_subnets("2001:db8::/32", 1000)
    assert pfx == 42 and len(rows) == 1000


def test_ip_to_binary():
    assert cidr.ip_to_binary("192.168.1.0") == "11000000.10101000.00000001.00000000"


def run_cli(capsys, *argv):
    with pytest.raises(SystemExit) as exc:
        cidr.main(list(argv))
        raise SystemExit(0)
    out = capsys.readouterr()
    return exc.value.code, out.out, out.err


def test_cli_json(capsys):
    code, out, _ = run_cli(capsys, "10.0.0.0/30", "--json")
    assert code == 0
    assert json.loads(out)["usable_hosts"] == 2


def test_cli_legacy_ip_flag(capsys):
    code, out, _ = run_cli(capsys, "-ip", "192.168.1.0/24", "-vertical")
    assert code == 0 and "192.168.1.254" in out
    assert "\033[" not in out  # plain when not a TTY


def test_cli_divide_json(capsys):
    code, out, _ = run_cli(capsys, "192.168.0.0/16", "-divide", "2", "--json")
    data = json.loads(out)
    assert data["new_prefix"] == 17 and len(data["subnets"]) == 2


def test_cli_binary_table(capsys):
    code, out, _ = run_cli(capsys, "192.168.1.0/24", "-divide", "2", "-binary")
    assert code == 0 and "11000000.10101000.00000001.10000000" in out


def test_cli_errors_go_to_stderr(capsys):
    code, out, err = run_cli(capsys, "nope")
    assert code == 1 and "Error" in err and out == ""
    code, _, err = run_cli(capsys, "10.0.0.0/24", "-divide", "0")
    assert code == 1 and "positive" in err
