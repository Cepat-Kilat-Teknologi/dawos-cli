"""Tests for all command modules — system, service, sessions, config, profile, network,
firewall, nat, traffic, pool, pppoe, routing, conntrack, scheduler, events, dhcp,
dns, monitoring, logs, ntp, lldp, vrrp, flow, limits, zone, diagnostics.

Each command is tested by mocking dawos_cli.client.get/post/put/delete and running
the CLI via Typer's CliRunner.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# System
# ═══════════════════════════════════════════════════════════════════════════════


class TestSystemCommands:
    def test_info(self, cli, mock_client):
        mock_client["get"].return_value = {"hostname": "bng1", "os": "linux"}
        result = cli("system", "info")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/system/info")

    def test_health(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "healthy"}
        result = cli("system", "health")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/health")

    def test_metrics(self, cli, mock_client):
        mock_client["get"].return_value = {"cpu": 10, "memory": 50}
        result = cli("system", "metrics")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/system/metrics")


# ═══════════════════════════════════════════════════════════════════════════════
# Service
# ═══════════════════════════════════════════════════════════════════════════════


class TestServiceCommands:
    def test_status(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "running"}
        result = cli("service", "status")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/service/status")

    def test_start(self, cli, mock_client):
        result = cli("service", "start")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/service/start")

    def test_stop(self, cli, mock_client):
        result = cli("service", "stop", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/service/stop")

    def test_restart(self, cli, mock_client):
        result = cli("service", "restart", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/service/restart")

    def test_cmd(self, cli, mock_client):
        mock_client["post"].return_value = {"output": "show stat output"}
        result = cli("service", "cmd", "show stat")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/service/command", json={"command": "show stat"}
        )

    def test_cmd_no_output_key(self, cli, mock_client):
        mock_client["post"].return_value = {"status": "ok"}
        result = cli("service", "cmd", "reload")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Sessions
# ═══════════════════════════════════════════════════════════════════════════════


class TestSessionCommands:
    def test_list(self, cli, mock_client):
        mock_client["get"].return_value = {
            "sessions": [
                {
                    "username": "user1",
                    "ip": "10.0.0.1",
                    "rate_limit": "10M/20M",
                    "type": "pppoe",
                    "state": "active",
                    "uptime": "1h",
                }
            ]
        }
        result = cli("session", "list")
        assert result.exit_code == 0

    def test_list_non_dict(self, cli, mock_client):
        mock_client["get"].return_value = [
            {
                "username": "user1",
                "ip": "10.0.0.1",
                "rate_limit": "10M",
                "type": "pppoe",
                "state": "active",
                "uptime": "1h",
            }
        ]
        result = cli("session", "list")
        assert result.exit_code == 0

    def test_list_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"error": "no data"}
        result = cli("session", "list")
        assert result.exit_code == 0

    def test_stats(self, cli, mock_client):
        mock_client["get"].return_value = {"active": 100}
        result = cli("session", "stats")
        assert result.exit_code == 0

    def test_find(self, cli, mock_client):
        mock_client["get"].return_value = {
            "sessions": [
                {
                    "username": "user1",
                    "ip": "10.0.0.1",
                    "rate_limit": "10M",
                    "type": "pppoe",
                    "state": "active",
                    "uptime": "1h",
                    "rx_bytes": 1000,
                    "tx_bytes": 2000,
                }
            ]
        }
        result = cli("session", "find", "user1")
        assert result.exit_code == 0

    def test_find_empty(self, cli, mock_client):
        mock_client["get"].return_value = {"sessions": []}
        result = cli("session", "find", "nobody")
        assert result.exit_code == 0

    def test_find_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"error": "fail"}
        result = cli("session", "find", "user1")
        assert result.exit_code == 0

    def test_terminate(self, cli, mock_client):
        result = cli("session", "terminate", "user1", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/sessions/terminate", json={"username": "user1"}
        )

    def test_by_sid(self, cli, mock_client):
        result = cli("session", "by-sid", "sid123")
        assert result.exit_code == 0

    def test_by_ip(self, cli, mock_client):
        result = cli("session", "by-ip", "10.0.0.1")
        assert result.exit_code == 0

    def test_snapshot(self, cli, mock_client):
        result = cli("session", "snapshot", "user1")
        assert result.exit_code == 0

    def test_restart(self, cli, mock_client):
        result = cli("session", "restart", "user1", "--force")
        assert result.exit_code == 0

    def test_drop_by_mac(self, cli, mock_client):
        result = cli("session", "drop-by-mac", "AA:BB:CC:DD:EE:FF", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════════════


class TestConfigCommands:
    def test_show(self, cli, mock_client):
        mock_client["get"].return_value = {"content": "[ppp]\nverbose=1"}
        result = cli("config", "show")
        assert result.exit_code == 0

    def test_show_no_content(self, cli, mock_client):
        mock_client["get"].return_value = {"key": "val"}
        result = cli("config", "show")
        assert result.exit_code == 0

    def test_update(self, cli, mock_client):
        result = cli("config", "update", "new config data", "--force")
        assert result.exit_code == 0

    def test_update_from_file(self, cli, mock_client, tmp_path):
        f = tmp_path / "config.txt"
        f.write_text("[ppp]\nverbose=1")
        result = cli("config", "update", f"@{f}", "--force")
        assert result.exit_code == 0

    def test_update_file_not_found(self, cli, mock_client):
        result = cli("config", "update", "@nonexistent.txt", "--force")
        assert result.exit_code == 1

    def test_backups(self, cli, mock_client):
        mock_client["get"].return_value = {"backups": ["backup1", "backup2"]}
        result = cli("config", "backups")
        assert result.exit_code == 0

    def test_backups_no_key(self, cli, mock_client):
        mock_client["get"].return_value = {"data": "x"}
        result = cli("config", "backups")
        assert result.exit_code == 0

    def test_revisions(self, cli, mock_client):
        mock_client["get"].return_value = {
            "revisions": [{"name": "r1", "timestamp": "now", "size": 100}]
        }
        result = cli("config", "revisions")
        assert result.exit_code == 0

    def test_revisions_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("config", "revisions")
        assert result.exit_code == 0

    def test_diff(self, cli, mock_client):
        mock_client["get"].return_value = {"diff": "+added\n-removed"}
        result = cli("config", "diff", "backup1")
        assert result.exit_code == 0

    def test_diff_no_key(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "no diff"}
        result = cli("config", "diff", "backup1")
        assert result.exit_code == 0

    def test_rollback(self, cli, mock_client):
        result = cli("config", "rollback", "backup1", "--force")
        assert result.exit_code == 0

    def test_apply(self, cli, mock_client):
        result = cli("config", "apply", "new config data", "--force")
        assert result.exit_code == 0

    def test_confirm(self, cli, mock_client):
        result = cli("config", "confirm")
        assert result.exit_code == 0

    def test_apply_status(self, cli, mock_client):
        result = cli("config", "apply-status")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Profile
# ═══════════════════════════════════════════════════════════════════════════════


class TestProfileCommands:
    def test_add_no_check(self, cli, mock_client, tmp_config):
        result = cli(
            "profile",
            "add",
            "bng1",
            "--url",
            "http://10.0.0.1:8470",
            "--key",
            "k",
            "--no-check",
        )
        assert result.exit_code == 0

    def test_add_with_check_success(self, cli, mock_client, tmp_config):
        mock_client["health"].return_value = {"node_name": "bng1", "version": "1.0"}
        result = cli(
            "profile", "add", "bng1", "--url", "http://10.0.0.1:8470", "--key", "k"
        )
        assert result.exit_code == 0

    def test_add_with_check_fail(self, cli, mock_client, tmp_config):
        mock_client["health"].return_value = None
        result = cli(
            "profile", "add", "bng1", "--url", "http://10.0.0.1:8470", "--key", "k"
        )
        assert result.exit_code == 1

    def test_add_warns_on_insecure_remote_url(self, cli, mock_client, tmp_config):
        """Plain HTTP to a non-loopback host warns about the unencrypted key."""
        result = cli(
            "profile",
            "add",
            "bng9",
            "--url",
            "http://10.0.0.9:8470",
            "--key",
            "k",
            "--no-check",
        )
        assert result.exit_code == 0
        assert "unencrypted" in result.output

    def test_add_no_warning_for_localhost(self, cli, mock_client, tmp_config):
        result = cli(
            "profile",
            "add",
            "local",
            "--url",
            "http://localhost:8470",
            "--key",
            "k",
            "--no-check",
        )
        assert result.exit_code == 0
        assert "unencrypted" not in result.output

    def test_add_no_warning_for_https(self, cli, mock_client, tmp_config):
        result = cli(
            "profile",
            "add",
            "secure",
            "--url",
            "https://10.0.0.9:8470",
            "--key",
            "k",
            "--no-check",
        )
        assert result.exit_code == 0
        assert "unencrypted" not in result.output

    def test_list_empty(self, cli, mock_client, tmp_config):
        result = cli("profile", "list")
        assert result.exit_code == 0

    def test_list_with_profiles(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        result = cli("profile", "list")
        assert result.exit_code == 0

    def test_remove_exists(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        result = cli("profile", "remove", "bng1")
        assert result.exit_code == 0

    def test_remove_not_found(self, cli, mock_client, tmp_config):
        result = cli("profile", "remove", "nope")
        assert result.exit_code == 1

    def test_use_exists(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        result = cli("profile", "use", "bng1")
        assert result.exit_code == 0

    def test_use_not_found(self, cli, mock_client, tmp_config):
        result = cli("profile", "use", "nope")
        assert result.exit_code == 1

    def test_test_ok(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        mock_client["health"].return_value = {"status": "ok"}
        result = cli("profile", "test", "bng1")
        assert result.exit_code == 0

    def test_test_fail(self, cli, mock_client, tmp_config):
        from dawos_cli import config

        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        mock_client["health"].return_value = None
        result = cli("profile", "test", "bng1")
        assert result.exit_code == 1

    def test_test_not_found(self, cli, mock_client, tmp_config):
        result = cli("profile", "test", "nope")
        assert result.exit_code == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Network
# ═══════════════════════════════════════════════════════════════════════════════


class TestNetworkCommands:
    def test_interfaces(self, cli, mock_client):
        mock_client["get"].return_value = {
            "interfaces": [
                {
                    "name": "eth0",
                    "state": "up",
                    "mac": "aa:bb",
                    "mtu": 1500,
                    "addresses": "10.0.0.1/24",
                }
            ]
        }
        result = cli("network", "interfaces")
        assert result.exit_code == 0

    def test_interfaces_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("network", "interfaces")
        assert result.exit_code == 0

    def test_interface_detail(self, cli, mock_client):
        result = cli("network", "interface", "eth0")
        assert result.exit_code == 0

    def test_interface_config(self, cli, mock_client):
        result = cli("network", "interface-config", "eth0", "--state", "up")
        assert result.exit_code == 0

    def test_interface_config_mtu(self, cli, mock_client):
        result = cli("network", "interface-config", "eth0", "--mtu", "9000")
        assert result.exit_code == 0

    def test_interface_config_no_opts(self, cli, mock_client):
        result = cli("network", "interface-config", "eth0")
        assert result.exit_code == 1

    def test_routes(self, cli, mock_client):
        mock_client["get"].return_value = {
            "routes": [
                {
                    "destination": "0.0.0.0/0",
                    "gateway": "10.0.0.1",
                    "interface": "eth0",
                    "metric": 100,
                    "protocol": "static",
                }
            ]
        }
        result = cli("network", "routes")
        assert result.exit_code == 0

    def test_add_route(self, cli, mock_client):
        result = cli("network", "add-route", "10.0.0.0/24", "--gw", "10.0.0.1")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/network/routes",
            json={"destination": "10.0.0.0/24", "gateway": "10.0.0.1"},
        )

    def test_add_route_with_dev(self, cli, mock_client):
        result = cli("network", "add-route", "10.0.0.0/24", "--dev", "eth0")
        assert result.exit_code == 0
        call_args = mock_client["post"].call_args
        assert call_args[1]["json"]["device"] == "eth0"

    def test_add_route_with_metric(self, cli, mock_client):
        result = cli("network", "add-route", "10.0.0.0/24", "--metric", "100")
        assert result.exit_code == 0

    def test_del_route(self, cli, mock_client):
        result = cli("network", "del-route", "10.0.0.0/24")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with(
            "/api/v1/network/routes", json={"destination": "10.0.0.0/24"}
        )

    def test_del_route_with_gw(self, cli, mock_client):
        result = cli("network", "del-route", "10.0.0.0/24", "--gw", "10.0.0.1")
        assert result.exit_code == 0

    def test_dns(self, cli, mock_client):
        result = cli("network", "dns")
        assert result.exit_code == 0

    def test_dns_set(self, cli, mock_client):
        result = cli("network", "dns-set", "8.8.8.8,1.1.1.1")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/network/dns", json={"nameservers": ["8.8.8.8", "1.1.1.1"]}
        )

    def test_vlans(self, cli, mock_client):
        mock_client["get"].return_value = {
            "vlans": [{"name": "eth0.100", "id": 100, "parent": "eth0", "state": "up"}]
        }
        result = cli("network", "vlans")
        assert result.exit_code == 0

    def test_vlan_add(self, cli, mock_client):
        result = cli("network", "vlan-add", "eth0", "--id", "100")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/network/vlans", json={"parent": "eth0", "vlan_id": 100}
        )

    def test_vlan_add_with_address(self, cli, mock_client):
        result = cli("network", "vlan-add", "eth0", "--id", "100", "-a", "10.0.0.1/24")
        assert result.exit_code == 0
        call_args = mock_client["post"].call_args
        assert call_args[1]["json"]["address"] == "10.0.0.1/24"

    def test_vlan_del(self, cli, mock_client):
        result = cli("network", "vlan-del", "eth0.100")
        assert result.exit_code == 0

    def test_vlan_state(self, cli, mock_client):
        result = cli("network", "vlan-state", "eth0.100", "up")
        assert result.exit_code == 0

    def test_throughput(self, cli, mock_client):
        mock_client["get"].return_value = {
            "rx_bytes": 123456789,
            "tx_bytes": 987654321,
            "rx_bps": 0.0,
            "tx_bps": 0.0,
            "interfaces": [
                {"name": "eth0", "rx_bytes": 100000000, "tx_bytes": 900000000},
                {"name": "eth1", "rx_bytes": 23456789, "tx_bytes": 87654321},
            ],
        }
        result = cli("network", "throughput")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/network/throughput")
        assert "eth0" in result.output

    def test_throughput_empty(self, cli, mock_client):
        mock_client["get"].return_value = {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "interfaces": [],
        }
        result = cli("network", "throughput")
        assert result.exit_code == 0

    def test_throughput_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("network", "throughput")
        assert result.exit_code == 0

    def test_throughput_large_values(self, cli, mock_client):
        """Cover the PB branch in _format_bytes."""
        mock_client["get"].return_value = {
            "rx_bytes": 0,
            "tx_bytes": 0,
            "interfaces": [
                {
                    "name": "eth0",
                    "rx_bytes": 2 * 1024**5,  # 2 PB
                    "tx_bytes": 500 * 1024**4,  # 500 TB
                },
            ],
        }
        result = cli("network", "throughput")
        assert result.exit_code == 0
        assert "PB" in result.output


# ═══════════════════════════════════════════════════════════════════════════════
# Firewall
# ═══════════════════════════════════════════════════════════════════════════════


class TestFirewallCommands:
    def test_status(self, cli, mock_client):
        result = cli("firewall", "status")
        assert result.exit_code == 0

    def test_rules(self, cli, mock_client):
        mock_client["get"].return_value = {"ruleset": "table inet filter {}"}
        result = cli("firewall", "rules")
        assert result.exit_code == 0

    def test_rules_no_ruleset(self, cli, mock_client):
        mock_client["get"].return_value = {"data": "x"}
        result = cli("firewall", "rules")
        assert result.exit_code == 0

    def test_save(self, cli, mock_client):
        result = cli("firewall", "save")
        assert result.exit_code == 0

    def test_validate(self, cli, mock_client):
        result = cli("firewall", "validate", "table inet filter {}")
        assert result.exit_code == 0

    def test_sysctl(self, cli, mock_client):
        result = cli("firewall", "sysctl")
        assert result.exit_code == 0

    def test_sysctl_set(self, cli, mock_client):
        result = cli("firewall", "sysctl-set", "net.ipv4.ip_forward", "1", "--force")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/firewall/sysctl",
            json={"key": "net.ipv4.ip_forward", "value": "1"},
        )

    def test_sysctl_set_confirm_accept(self, cli, mock_client):
        result = cli("firewall", "sysctl-set", "net.ipv4.ip_forward", "1", input="y\n")
        assert result.exit_code == 0
        mock_client["put"].assert_called_once()

    def test_sysctl_set_confirm_abort(self, cli, mock_client):
        result = cli("firewall", "sysctl-set", "net.ipv4.ip_forward", "1", input="n\n")
        assert result.exit_code != 0
        mock_client["put"].assert_not_called()

    def test_conntrack(self, cli, mock_client):
        result = cli("firewall", "conntrack")
        assert result.exit_code == 0

    def test_conntrack_set(self, cli, mock_client):
        result = cli("firewall", "conntrack-set", "262144")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/firewall/conntrack", json={"max_value": 262144}
        )

    def test_snmp(self, cli, mock_client):
        result = cli("firewall", "snmp")
        assert result.exit_code == 0

    def test_groups(self, cli, mock_client):
        mock_client["get"].return_value = {
            "groups": [
                {"name": "blocked", "group_type": "address", "elements": "1.2.3.4"}
            ]
        }
        result = cli("firewall", "groups")
        assert result.exit_code == 0

    def test_groups_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("firewall", "groups")
        assert result.exit_code == 0

    def test_group_add(self, cli, mock_client):
        result = cli("firewall", "group-add", "blocked", "--type", "address")
        assert result.exit_code == 0

    def test_group_add_with_elements(self, cli, mock_client):
        result = cli(
            "firewall",
            "group-add",
            "blocked",
            "--type",
            "address",
            "-e",
            "1.2.3.4,5.6.7.8",
        )
        assert result.exit_code == 0

    def test_group_del(self, cli, mock_client):
        result = cli("firewall", "group-del", "blocked", "--force")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with("/api/v1/firewall/groups/blocked")

    def test_group_del_confirm_accept(self, cli, mock_client):
        result = cli("firewall", "group-del", "blocked", input="y\n")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_once()

    def test_group_del_confirm_abort(self, cli, mock_client):
        result = cli("firewall", "group-del", "blocked", input="n\n")
        assert result.exit_code != 0
        mock_client["delete"].assert_not_called()

    def test_group_members(self, cli, mock_client):
        result = cli("firewall", "group-members", "blocked", "1.2.3.4,5.6.7.8")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# NAT
# ═══════════════════════════════════════════════════════════════════════════════


class TestNatCommands:
    def test_status(self, cli, mock_client):
        result = cli("nat", "status")
        assert result.exit_code == 0

    def test_masquerade_on(self, cli, mock_client):
        result = cli("nat", "masquerade-on", "eth0")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/firewall/nat/masquerade", json={"wan_interface": "eth0"}
        )

    def test_masquerade_off(self, cli, mock_client):
        result = cli("nat", "masquerade-off", "eth0", "--force")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with(
            "/api/v1/firewall/nat/masquerade", json={"wan_interface": "eth0"}
        )

    def test_masquerade_off_confirm_accept(self, cli, mock_client):
        result = cli("nat", "masquerade-off", "eth0", input="y\n")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_once()

    def test_masquerade_off_confirm_abort(self, cli, mock_client):
        result = cli("nat", "masquerade-off", "eth0", input="n\n")
        assert result.exit_code != 0
        mock_client["delete"].assert_not_called()

    def test_egress(self, cli, mock_client):
        result = cli("nat", "egress")
        assert result.exit_code == 0

    def test_egress_set(self, cli, mock_client):
        result = cli("nat", "egress-set", "10.0.0.1", "1.2.3.4")
        assert result.exit_code == 0

    def test_egress_del(self, cli, mock_client):
        result = cli("nat", "egress-del", "10.0.0.1", "--force")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with("/api/v1/firewall/nat/egress/10.0.0.1")

    def test_egress_del_confirm_abort(self, cli, mock_client):
        result = cli("nat", "egress-del", "10.0.0.1", input="n\n")
        assert result.exit_code != 0
        mock_client["delete"].assert_not_called()

    def test_public_ip_add(self, cli, mock_client):
        result = cli("nat", "public-ip-add", "1.2.3.4")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/firewall/nat/public-ip", json={"public_ip": "1.2.3.4"}
        )

    def test_public_ip_del(self, cli, mock_client):
        result = cli("nat", "public-ip-del", "1.2.3.4", "--force")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with(
            "/api/v1/firewall/nat/public-ip/1.2.3.4"
        )

    def test_public_ip_del_confirm_abort(self, cli, mock_client):
        result = cli("nat", "public-ip-del", "1.2.3.4", input="n\n")
        assert result.exit_code != 0
        mock_client["delete"].assert_not_called()

    def test_box_egress(self, cli, mock_client):
        result = cli("nat", "box-egress")
        assert result.exit_code == 0

    def test_box_egress_set_on(self, cli, mock_client):
        result = cli("nat", "box-egress-set", "true")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/firewall/nat/box-egress", json={"action": "on"}
        )

    def test_box_egress_set_off(self, cli, mock_client):
        result = cli("nat", "box-egress-set", "false")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/firewall/nat/box-egress", json={"action": "off"}
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Traffic
# ═══════════════════════════════════════════════════════════════════════════════


class TestTrafficCommands:
    def test_queue(self, cli, mock_client):
        result = cli("traffic", "queue", "user1")
        assert result.exit_code == 0

    def test_ratelimit(self, cli, mock_client):
        result = cli("traffic", "ratelimit", "user1", "5M/20M")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/traffic/ratelimit/user1", json={"rate": "5M/20M"}
        )

    def test_ratelimit_restore(self, cli, mock_client):
        result = cli("traffic", "ratelimit-restore", "user1")
        assert result.exit_code == 0
        mock_client["delete"].assert_called_with("/api/v1/traffic/ratelimit/user1")

    def test_watch(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(
            ['{"username": "user1", "download_mbps": 10.5, "upload_mbps": 2.3}']
        )
        result = cli("traffic", "watch")
        assert result.exit_code == 0

    def test_watch_invalid_json(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(["not json"])
        result = cli("traffic", "watch")
        assert result.exit_code == 0

    def test_watch_non_dict(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(['"just a string"'])
        result = cli("traffic", "watch")
        assert result.exit_code == 0

    def test_watch_user(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(
            ['{"download_mbps": 5.0, "upload_mbps": 1.0}']
        )
        result = cli("traffic", "watch-user", "user1")
        assert result.exit_code == 0

    def test_watch_user_invalid_json(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(["bad"])
        result = cli("traffic", "watch-user", "user1")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Pool
# ═══════════════════════════════════════════════════════════════════════════════


class TestPoolCommands:
    def test_list(self, cli, mock_client):
        mock_client["get"].return_value = {
            "pools": [
                {
                    "name": "pool1",
                    "subnet": "10.0.0.0/24",
                    "used": 10,
                    "available": 244,
                    "total": 254,
                }
            ]
        }
        result = cli("pool", "list")
        assert result.exit_code == 0

    def test_list_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("pool", "list")
        assert result.exit_code == 0

    def test_usage(self, cli, mock_client):
        result = cli("pool", "usage")
        assert result.exit_code == 0

    def test_add(self, cli, mock_client):
        result = cli("pool", "add", "pool1", "10.0.0.0/24")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/ip-pool", json={"name": "pool1", "ip_range": "10.0.0.0/24"}
        )

    def test_remove(self, cli, mock_client):
        result = cli("pool", "remove", "pool1", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# PPPoE
# ═══════════════════════════════════════════════════════════════════════════════


class TestPppoeCommands:
    def test_interfaces(self, cli, mock_client):
        mock_client["get"].return_value = {
            "interfaces": [{"name": "eth1", "status": "up", "sessions": 50}]
        }
        result = cli("pppoe", "interfaces")
        assert result.exit_code == 0

    def test_interfaces_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("pppoe", "interfaces")
        assert result.exit_code == 0

    def test_add(self, cli, mock_client):
        result = cli("pppoe", "add", "eth2")
        assert result.exit_code == 0

    def test_remove(self, cli, mock_client):
        result = cli("pppoe", "remove", "eth2")
        assert result.exit_code == 0

    def test_mac_filter(self, cli, mock_client):
        mock_client["get"].return_value = {
            "entries": [{"mac": "AA:BB:CC:DD:EE:FF", "action": "allow"}]
        }
        result = cli("pppoe", "mac-filter")
        assert result.exit_code == 0

    def test_mac_filter_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("pppoe", "mac-filter")
        assert result.exit_code == 0

    def test_mac_add(self, cli, mock_client):
        result = cli("pppoe", "mac-add", "AA:BB:CC:DD:EE:FF")
        assert result.exit_code == 0

    def test_mac_del(self, cli, mock_client):
        result = cli("pppoe", "mac-del", "AA:BB:CC:DD:EE:FF")
        assert result.exit_code == 0

    def test_pado(self, cli, mock_client):
        result = cli("pppoe", "pado")
        assert result.exit_code == 0

    def test_pado_set(self, cli, mock_client):
        result = cli("pppoe", "pado-set", "500")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Routing
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoutingCommands:
    def test_bgp(self, cli, mock_client):
        result = cli("routing", "bgp")
        assert result.exit_code == 0

    def test_bgp_routes(self, cli, mock_client):
        mock_client["get"].return_value = {
            "routes": [
                {
                    "prefix": "10.0.0.0/24",
                    "next_hop": "10.0.0.1",
                    "metric": 0,
                    "as_path": "65000",
                    "status": "*>",
                }
            ]
        }
        result = cli("routing", "bgp-routes")
        assert result.exit_code == 0

    def test_bgp_routes_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("routing", "bgp-routes")
        assert result.exit_code == 0

    def test_ospf(self, cli, mock_client):
        result = cli("routing", "ospf")
        assert result.exit_code == 0

    def test_ospf_neighbors(self, cli, mock_client):
        mock_client["get"].return_value = {
            "neighbors": [
                {
                    "neighbor_id": "1.1.1.1",
                    "state": "Full",
                    "address": "10.0.0.2",
                    "interface": "eth0",
                    "dead_time": "30s",
                }
            ]
        }
        result = cli("routing", "ospf-neighbors")
        assert result.exit_code == 0

    def test_ospf_neighbors_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("routing", "ospf-neighbors")
        assert result.exit_code == 0

    def test_ospf_routes(self, cli, mock_client):
        result = cli("routing", "ospf-routes")
        assert result.exit_code == 0

    def test_rip(self, cli, mock_client):
        result = cli("routing", "rip")
        assert result.exit_code == 0

    def test_rip_routes(self, cli, mock_client):
        result = cli("routing", "rip-routes")
        assert result.exit_code == 0

    def test_bfd(self, cli, mock_client):
        result = cli("routing", "bfd")
        assert result.exit_code == 0

    def test_bfd_peers(self, cli, mock_client):
        mock_client["get"].return_value = {
            "peers": [
                {
                    "peer": "10.0.0.1",
                    "status": "up",
                    "interface": "eth0",
                    "uptime": "1h",
                }
            ]
        }
        result = cli("routing", "bfd-peers")
        assert result.exit_code == 0

    def test_bfd_peers_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("routing", "bfd-peers")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Conntrack
# ═══════════════════════════════════════════════════════════════════════════════


class TestConntrackCommands:
    def test_config(self, cli, mock_client):
        result = cli("conntrack", "config")
        assert result.exit_code == 0

    def test_table_size_show(self, cli, mock_client):
        result = cli("conntrack", "table-size")
        assert result.exit_code == 0
        mock_client["get"].assert_called()

    def test_table_size_set(self, cli, mock_client):
        result = cli("conntrack", "table-size", "262144")
        assert result.exit_code == 0
        mock_client["put"].assert_called()

    def test_timeouts(self, cli, mock_client):
        result = cli("conntrack", "timeouts")
        assert result.exit_code == 0

    def test_timeout_set(self, cli, mock_client):
        result = cli("conntrack", "timeout-set", "tcp_timeout_established", "7200")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/conntrack/timeouts",
            json={"key": "tcp_timeout_established", "seconds": 7200},
        )

    def test_helpers(self, cli, mock_client):
        mock_client["get"].return_value = {
            "helpers": [{"name": "ftp", "protocol": "tcp", "port": 21}]
        }
        result = cli("conntrack", "helpers")
        assert result.exit_code == 0

    def test_helpers_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("conntrack", "helpers")
        assert result.exit_code == 0

    def test_profiles(self, cli, mock_client):
        result = cli("conntrack", "profiles")
        assert result.exit_code == 0

    def test_profile_apply(self, cli, mock_client):
        result = cli("conntrack", "profile-apply", "isp-optimized")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/conntrack/profiles/apply", json={"name": "isp-optimized"}
        )

    def test_flush_force(self, cli, mock_client):
        mock_client["post"].return_value = {
            "success": True,
            "message": "Conntrack table flushed",
            "entries_before": 1234,
        }
        result = cli("conntrack", "flush", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/conntrack/flush")
        assert "1234" in result.output

    def test_flush_confirm_accept(self, cli, mock_client):
        mock_client["post"].return_value = {
            "success": True,
            "message": "Conntrack table flushed",
            "entries_before": 500,
        }
        result = cli("conntrack", "flush", input="y\n")
        assert result.exit_code == 0
        mock_client["post"].assert_called_once()

    def test_flush_confirm_abort(self, cli, mock_client):
        result = cli("conntrack", "flush", input="n\n")
        assert result.exit_code != 0
        mock_client["post"].assert_not_called()


# ═══════════════════════════════════════════════════════════════════════════════
# Scheduler
# ═══════════════════════════════════════════════════════════════════════════════


class TestSchedulerCommands:
    def test_list(self, cli, mock_client):
        mock_client["get"].return_value = {
            "jobs": [
                {
                    "name": "backup",
                    "command": "backup.sh",
                    "interval_seconds": 3600,
                    "enabled": True,
                    "last_run": "never",
                }
            ]
        }
        result = cli("scheduler", "list")
        assert result.exit_code == 0

    def test_list_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("scheduler", "list")
        assert result.exit_code == 0

    def test_add(self, cli, mock_client):
        result = cli("scheduler", "add", "backup", "-c", "backup.sh", "-i", "3600")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/scheduler/jobs",
            json={
                "name": "backup",
                "command": "backup.sh",
                "interval_seconds": 3600,
                "enabled": True,
            },
        )

    def test_add_disabled(self, cli, mock_client):
        result = cli("scheduler", "add", "job1", "-c", "cmd", "-i", "60", "--disabled")
        assert result.exit_code == 0
        call_args = mock_client["post"].call_args
        assert call_args[1]["json"]["enabled"] is False

    def test_remove(self, cli, mock_client):
        result = cli("scheduler", "remove", "backup")
        assert result.exit_code == 0

    def test_run(self, cli, mock_client):
        result = cli("scheduler", "run", "backup")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════════════


class TestEventsCommands:
    def test_hooks(self, cli, mock_client):
        mock_client["get"].return_value = {
            "hooks": [
                {
                    "name": "h1",
                    "event": "session-up",
                    "action": "http://webhook.com",
                    "url": "http://webhook.com",
                }
            ]
        }
        result = cli("events", "hooks")
        assert result.exit_code == 0

    def test_hooks_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("events", "hooks")
        assert result.exit_code == 0

    def test_hook_add(self, cli, mock_client):
        result = cli(
            "events", "hook-add", "h1", "-e", "session-up", "-a", "http://webhook.com"
        )
        assert result.exit_code == 0

    def test_hook_del(self, cli, mock_client):
        result = cli("events", "hook-del", "h1")
        assert result.exit_code == 0

    def test_fire(self, cli, mock_client):
        result = cli("events", "fire", "test-event")
        assert result.exit_code == 0

    def test_fire_with_payload(self, cli, mock_client):
        result = cli("events", "fire", "test-event", "-d", '{"key": "val"}')
        assert result.exit_code == 0

    def test_fire_invalid_json(self, cli, mock_client):
        result = cli("events", "fire", "test-event", "-d", "not json")
        assert result.exit_code == 1

    def test_history(self, cli, mock_client):
        mock_client["get"].return_value = {
            "entries": [
                {
                    "timestamp": "now",
                    "event": "session-up",
                    "hook": "h1",
                    "status": "ok",
                    "duration_ms": 10,
                }
            ]
        }
        result = cli("events", "history")
        assert result.exit_code == 0

    def test_history_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("events", "history")
        assert result.exit_code == 0

    def test_history_clear(self, cli, mock_client):
        result = cli("events", "history-clear", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# DHCP
# ═══════════════════════════════════════════════════════════════════════════════


class TestDhcpCommands:
    def test_status(self, cli, mock_client):
        result = cli("dhcp", "status")
        assert result.exit_code == 0

    def test_leases(self, cli, mock_client):
        mock_client["get"].return_value = {
            "leases": [
                {
                    "ip": "10.0.0.1",
                    "mac": "aa:bb",
                    "hostname": "h1",
                    "expires": "1h",
                    "interface": "eth0",
                }
            ]
        }
        result = cli("dhcp", "leases")
        assert result.exit_code == 0

    def test_leases_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("dhcp", "leases")
        assert result.exit_code == 0

    def test_relay(self, cli, mock_client):
        result = cli("dhcp", "relay")
        assert result.exit_code == 0

    def test_restart(self, cli, mock_client):
        result = cli("dhcp", "restart", "--force")
        assert result.exit_code == 0

    def test_relay_restart(self, cli, mock_client):
        result = cli("dhcp", "relay-restart", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# DNS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDnsCommands:
    def test_status(self, cli, mock_client):
        result = cli("dns", "status")
        assert result.exit_code == 0

    def test_config(self, cli, mock_client):
        result = cli("dns", "config")
        assert result.exit_code == 0

    def test_config_set_servers(self, cli, mock_client):
        result = cli("dns", "config-set", "-s", "8.8.8.8,1.1.1.1")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/dns/forwarding/config", json={"servers": ["8.8.8.8", "1.1.1.1"]}
        )

    def test_config_set_cache(self, cli, mock_client):
        result = cli("dns", "config-set", "--cache-size", "10000")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/dns/forwarding/config", json={"cache_size": 10000}
        )

    def test_config_set_no_opts(self, cli, mock_client):
        result = cli("dns", "config-set")
        assert result.exit_code == 1

    def test_flush(self, cli, mock_client):
        result = cli("dns", "flush")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Monitoring
# ═══════════════════════════════════════════════════════════════════════════════


class TestMonitoringCommands:
    def test_status(self, cli, mock_client):
        result = cli("monitoring", "status")
        assert result.exit_code == 0

    def test_metrics(self, cli, mock_client):
        result = cli("monitoring", "metrics", "accel-ppp")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/monitoring/metrics/accel-ppp")

    def test_metrics_service(self, cli, mock_client):
        result = cli("monitoring", "metrics-service", "frr")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/monitoring/metrics/frr")

    def test_configure(self, cli, mock_client):
        result = cli("monitoring", "configure", "-s", "accel-ppp", "--enable")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/monitoring/configure",
            json={"service": "accel-ppp", "enable": True},
        )

    def test_configure_disable(self, cli, mock_client):
        result = cli("monitoring", "configure", "-s", "prometheus", "--disable")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/monitoring/configure",
            json={"service": "prometheus", "enable": False},
        )

    def test_restart(self, cli, mock_client):
        result = cli("monitoring", "restart", "prometheus", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Logs
# ═══════════════════════════════════════════════════════════════════════════════


class TestLogsCommands:
    def test_tail(self, cli, mock_client):
        mock_client["get"].return_value = {
            "lines": [
                {
                    "timestamp": "now",
                    "service": "accel",
                    "message": "started",
                    "level": "info",
                }
            ]
        }
        result = cli("logs", "tail")
        assert result.exit_code == 0

    def test_tail_with_service(self, cli, mock_client):
        mock_client["get"].return_value = {"lines": []}
        result = cli("logs", "tail", "-s", "accel-ppp")
        assert result.exit_code == 0

    def test_tail_string_lines(self, cli, mock_client):
        mock_client["get"].return_value = {"lines": ["raw log line"]}
        result = cli("logs", "tail")
        assert result.exit_code == 0

    def test_tail_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"data": "x"}
        result = cli("logs", "tail")
        assert result.exit_code == 0

    def test_tail_levels(self, cli, mock_client):
        mock_client["get"].return_value = {
            "lines": [
                {"timestamp": "t", "service": "s", "message": "err", "level": "error"},
                {
                    "timestamp": "t",
                    "service": "s",
                    "message": "warn",
                    "level": "warning",
                },
                {"timestamp": "t", "service": "s", "message": "dbg", "level": "debug"},
            ]
        }
        result = cli("logs", "tail")
        assert result.exit_code == 0

    def test_stream(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(
            [
                '{"timestamp": "now", "service": "accel",'
                ' "message": "log", "level": "info"}'
            ]
        )
        result = cli("logs", "stream")
        assert result.exit_code == 0

    def test_stream_with_service(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter([])
        result = cli("logs", "stream", "-s", "accel-ppp")
        assert result.exit_code == 0

    def test_stream_non_dict(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(['"just a string"'])
        result = cli("logs", "stream")
        assert result.exit_code == 0

    def test_stream_invalid_json(self, cli, mock_client):
        mock_client["stream_sse"].return_value = iter(["bad json"])
        result = cli("logs", "stream")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# NTP
# ═══════════════════════════════════════════════════════════════════════════════


class TestNtpCommands:
    def test_status(self, cli, mock_client):
        result = cli("ntp", "status")
        assert result.exit_code == 0

    def test_sources(self, cli, mock_client):
        mock_client["get"].return_value = {
            "sources": [
                {
                    "server": "ntp.pool.org",
                    "stratum": 2,
                    "offset": "0.5ms",
                    "delay": "10ms",
                    "jitter": "0.1ms",
                    "reach": 377,
                }
            ]
        }
        result = cli("ntp", "sources")
        assert result.exit_code == 0

    def test_sources_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("ntp", "sources")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# LLDP
# ═══════════════════════════════════════════════════════════════════════════════


class TestLldpCommands:
    def test_status(self, cli, mock_client):
        result = cli("lldp", "status")
        assert result.exit_code == 0

    def test_neighbors(self, cli, mock_client):
        mock_client["get"].return_value = {
            "neighbors": [
                {
                    "local_port": "eth0",
                    "chassis_id": "aa:bb",
                    "system_name": "switch1",
                    "port_id": "ge0/1",
                    "management_address": "10.0.0.1",
                    "ttl": 120,
                }
            ]
        }
        result = cli("lldp", "neighbors")
        assert result.exit_code == 0

    def test_neighbors_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("lldp", "neighbors")
        assert result.exit_code == 0

    def test_neighbor(self, cli, mock_client):
        result = cli("lldp", "neighbor", "eth0")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# VRRP
# ═══════════════════════════════════════════════════════════════════════════════


class TestVrrpCommands:
    def test_status(self, cli, mock_client):
        result = cli("vrrp", "status")
        assert result.exit_code == 0

    def test_group(self, cli, mock_client):
        result = cli("vrrp", "group", "vrrp1")
        assert result.exit_code == 0

    def test_failover(self, cli, mock_client):
        result = cli("vrrp", "failover", "vrrp1", "--force")
        assert result.exit_code == 0

    def test_restart(self, cli, mock_client):
        result = cli("vrrp", "restart", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Flow
# ═══════════════════════════════════════════════════════════════════════════════


class TestFlowCommands:
    def test_status(self, cli, mock_client):
        result = cli("flow", "status")
        assert result.exit_code == 0

    def test_collectors(self, cli, mock_client):
        mock_client["get"].return_value = {
            "collectors": [
                {
                    "name": "c1",
                    "address": "10.0.0.1",
                    "port": 2055,
                    "protocol": "netflow",
                    "status": "active",
                }
            ]
        }
        result = cli("flow", "collectors")
        assert result.exit_code == 0

    def test_collectors_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("flow", "collectors")
        assert result.exit_code == 0

    def test_stats(self, cli, mock_client):
        result = cli("flow", "stats")
        assert result.exit_code == 0

    def test_restart(self, cli, mock_client):
        result = cli("flow", "restart", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Limits
# ═══════════════════════════════════════════════════════════════════════════════


class TestLimitsCommands:
    def test_show(self, cli, mock_client):
        result = cli("limits", "show")
        assert result.exit_code == 0

    def test_set_max_sessions(self, cli, mock_client):
        result = cli("limits", "set", "--max-sessions", "1000")
        assert result.exit_code == 0
        mock_client["put"].assert_called_with(
            "/api/v1/limits", json={"max_sessions": 1000}
        )

    def test_set_max_starting(self, cli, mock_client):
        result = cli("limits", "set", "--max-starting", "50")
        assert result.exit_code == 0

    def test_set_no_opts(self, cli, mock_client):
        result = cli("limits", "set")
        assert result.exit_code == 1

    def test_interface(self, cli, mock_client):
        result = cli("limits", "interface", "eth0")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Zone
# ═══════════════════════════════════════════════════════════════════════════════


class TestZoneCommands:
    def test_list(self, cli, mock_client):
        mock_client["get"].return_value = {
            "zones": [
                {
                    "name": "trusted",
                    "interfaces": "eth0",
                    "default_action": "accept",
                    "rules_count": 5,
                }
            ]
        }
        result = cli("zone", "list")
        assert result.exit_code == 0

    def test_list_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("zone", "list")
        assert result.exit_code == 0

    def test_show(self, cli, mock_client):
        result = cli("zone", "show", "trusted")
        assert result.exit_code == 0

    def test_add(self, cli, mock_client):
        result = cli("zone", "add", "dmz", "--default-action", "drop")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/zones", json={"name": "dmz", "default_action": "drop"}
        )

    def test_remove(self, cli, mock_client):
        result = cli("zone", "remove", "dmz", "--force")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Diagnostics
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiagnosticsCommands:
    def test_doctor_ok(self, cli, mock_client):
        mock_client["get"].return_value = {
            "checks": [
                {"name": "disk", "status": "ok", "detail": "50% used"},
                {"name": "memory", "status": "warning", "detail": "80% used"},
                {"name": "config", "status": "error", "detail": "invalid"},
            ]
        }
        result = cli("diagnostics", "doctor")
        assert result.exit_code == 0

    def test_doctor_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok"}
        result = cli("diagnostics", "doctor")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Coverage: confirm prompts (without --yes flag — user answers "y")
# ═══════════════════════════════════════════════════════════════════════════════


class TestConfirmPrompts:
    """Cover typer.confirm() lines that only execute when --yes is not passed."""

    def test_service_stop_confirm(self, cli, mock_client):
        result = cli("service", "stop", input="y\n")
        assert result.exit_code == 0

    def test_service_restart_confirm(self, cli, mock_client):
        result = cli("service", "restart", input="y\n")
        assert result.exit_code == 0

    def test_session_terminate_confirm(self, cli, mock_client):
        result = cli("session", "terminate", "sess-123", input="y\n")
        assert result.exit_code == 0

    def test_session_restart_confirm(self, cli, mock_client):
        result = cli("session", "restart", "user1", input="y\n")
        assert result.exit_code == 0

    def test_session_drop_by_mac_confirm(self, cli, mock_client):
        result = cli("session", "drop-by-mac", "aa:bb:cc:dd:ee:ff", input="y\n")
        assert result.exit_code == 0

    def test_config_update_confirm(self, cli, mock_client, tmp_path):
        cfg_file = tmp_path / "accel.conf"
        cfg_file.write_text("[general]\n")
        result = cli("config", "update", str(cfg_file), input="y\n")
        assert result.exit_code == 0

    def test_config_rollback_confirm(self, cli, mock_client):
        result = cli("config", "rollback", "backup-1", input="y\n")
        assert result.exit_code == 0

    def test_config_apply_guarded_confirm(self, cli, mock_client):
        result = cli("config", "apply", "test config", input="y\n")
        assert result.exit_code == 0

    def test_dhcp_restart_confirm(self, cli, mock_client):
        result = cli("dhcp", "restart", input="y\n")
        assert result.exit_code == 0

    def test_dhcp_relay_restart_confirm(self, cli, mock_client):
        result = cli("dhcp", "relay-restart", input="y\n")
        assert result.exit_code == 0

    def test_events_history_clear_confirm(self, cli, mock_client):
        result = cli("events", "history-clear", input="y\n")
        assert result.exit_code == 0

    def test_flow_restart_confirm(self, cli, mock_client):
        result = cli("flow", "restart", input="y\n")
        assert result.exit_code == 0

    def test_monitoring_restart_confirm(self, cli, mock_client):
        result = cli("monitoring", "restart", "prometheus", input="y\n")
        assert result.exit_code == 0

    def test_pool_remove_confirm(self, cli, mock_client):
        result = cli("pool", "remove", "pool1", input="y\n")
        assert result.exit_code == 0

    def test_vrrp_failover_confirm(self, cli, mock_client):
        result = cli("vrrp", "failover", "group1", input="y\n")
        assert result.exit_code == 0

    def test_vrrp_restart_confirm(self, cli, mock_client):
        result = cli("vrrp", "restart", input="y\n")
        assert result.exit_code == 0

    def test_zone_delete_confirm(self, cli, mock_client):
        result = cli("zone", "remove", "dmz", input="y\n")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Coverage: KeyboardInterrupt for streaming commands
# ═══════════════════════════════════════════════════════════════════════════════


class TestStreamInterrupt:
    """Cover KeyboardInterrupt handlers in traffic watch/watch-user and logs stream."""

    def test_traffic_watch_interrupt(self, cli, mock_client):
        mock_client["stream_sse"].side_effect = KeyboardInterrupt()
        result = cli("traffic", "watch")
        assert result.exit_code == 0

    def test_traffic_watch_user_interrupt(self, cli, mock_client):
        mock_client["stream_sse"].side_effect = KeyboardInterrupt()
        result = cli("traffic", "watch-user", "john")
        assert result.exit_code == 0

    def test_logs_stream_interrupt(self, cli, mock_client):
        mock_client["stream_sse"].side_effect = KeyboardInterrupt()
        result = cli("logs", "stream")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Coverage: non-list response paths for routes/vlans
# ═══════════════════════════════════════════════════════════════════════════════


class TestNetworkEdgeCases:
    """Cover the else branch when routes/vlans data is not a list."""

    def test_routes_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok", "info": "no routes"}
        result = cli("network", "routes")
        assert result.exit_code == 0

    def test_vlans_non_list(self, cli, mock_client):
        mock_client["get"].return_value = {"status": "ok", "info": "no vlans"}
        result = cli("network", "vlans")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# System — ready (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSystemReady:
    def test_ready(self, cli, mock_client):
        mock_client["get"].return_value = {"ready": True, "accel_ppp": "running"}
        result = cli("system", "ready")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/health/ready")


# ═══════════════════════════════════════════════════════════════════════════════
# Service — shutdown / shutdown-cancel (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestServiceShutdown:
    def test_shutdown_soft(self, cli, mock_client):
        mock_client["post"].return_value = {
            "message": "Shutdown (soft) initiated",
            "active_sessions": 5,
        }
        result = cli("service", "shutdown", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/service/shutdown",
            json={"mode": "soft", "confirm": True},
        )

    def test_shutdown_hard(self, cli, mock_client):
        mock_client["post"].return_value = {
            "message": "Shutdown (hard) initiated",
            "active_sessions": 0,
        }
        result = cli("service", "shutdown", "--mode", "hard", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/service/shutdown",
            json={"mode": "hard", "confirm": True},
        )

    def test_shutdown_cancel(self, cli, mock_client):
        mock_client["post"].return_value = {
            "message": "Shutdown cancelled",
            "active_sessions": 3,
        }
        result = cli("service", "shutdown-cancel")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/service/shutdown/cancel")

    def test_shutdown_confirm_abort(self, cli, mock_client):
        result = cli("service", "shutdown", input="n\n")
        assert result.exit_code != 0


# ═══════════════════════════════════════════════════════════════════════════════
# Config — revision-content / compare (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestConfigRevisionContent:
    def test_revision_content(self, cli, mock_client):
        mock_client["get"].return_value = {"content": "[ppp]\nverbose=1\n"}
        result = cli("config", "revision-content", "rev_20260101.conf")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with(
            "/api/v1/config/revisions/rev_20260101.conf/content"
        )
        assert "verbose=1" in result.output

    def test_revision_content_no_content_key(self, cli, mock_client):
        mock_client["get"].return_value = {"error": "not found"}
        result = cli("config", "revision-content", "missing.conf")
        assert result.exit_code == 0

    def test_compare(self, cli, mock_client):
        mock_client["get"].return_value = {
            "diff": "--- a\n+++ b\n@@ -1 +1 @@\n-old\n+new"
        }
        result = cli("config", "compare", "--from", "rev_a.conf", "--to", "rev_b.conf")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with(
            "/api/v1/config/compare", from_name="rev_a.conf", to_name="rev_b.conf"
        )
        assert "old" in result.output

    def test_compare_no_diff_key(self, cli, mock_client):
        mock_client["get"].return_value = {"message": "identical"}
        result = cli("config", "compare", "--from", "a", "--to", "b")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Audit (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuditCommands:
    def test_list_default(self, cli, mock_client):
        mock_client["get"].return_value = {
            "count": 2,
            "entries": [
                {
                    "timestamp": "2026-01-01T00:00:00Z",
                    "method": "POST",
                    "path": "/api/v1/service/restart",
                    "role": "admin",
                    "status": 200,
                    "duration_ms": 42,
                },
                {
                    "timestamp": "2026-01-01T00:01:00Z",
                    "method": "DELETE",
                    "path": "/api/v1/pool/1",
                    "role": "admin",
                    "status": 200,
                    "duration_ms": 15,
                },
            ],
        }
        result = cli("audit", "list")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/audit", limit=100)

    def test_list_with_filters(self, cli, mock_client):
        mock_client["get"].return_value = {"count": 0, "entries": []}
        result = cli(
            "audit",
            "list",
            "--limit",
            "10",
            "--method",
            "POST",
            "--path",
            "/api/v1/service",
            "--role",
            "admin",
            "--status",
            "200",
        )
        assert result.exit_code == 0
        mock_client["get"].assert_called_with(
            "/api/v1/audit",
            limit=10,
            method="POST",
            path="/api/v1/service",
            role="admin",
            status=200,
        )

    def test_list_non_dict(self, cli, mock_client):
        mock_client["get"].return_value = [{"timestamp": "t", "method": "GET"}]
        result = cli("audit", "list")
        assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
# Bulk (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestBulkCommands:
    def test_terminate(self, cli, mock_client):
        mock_client["post"].return_value = {
            "operation": "terminate",
            "total": 2,
            "succeeded": 2,
            "failed": 0,
            "results": [
                {"target": "user1", "success": True, "error": None},
                {"target": "user2", "success": True, "error": None},
            ],
        }
        result = cli("bulk", "terminate", "user1,user2", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/bulk/terminate",
            json={"usernames": ["user1", "user2"]},
        )
        assert "2 succeeded" in result.output

    def test_terminate_confirm_abort(self, cli, mock_client):
        result = cli("bulk", "terminate", "user1", input="n\n")
        assert result.exit_code != 0

    def test_ratelimit(self, cli, mock_client):
        mock_client["post"].return_value = {
            "operation": "ratelimit",
            "total": 2,
            "succeeded": 1,
            "failed": 1,
            "results": [
                {"target": "u1", "success": True, "error": None},
                {"target": "u2", "success": False, "error": "not found"},
            ],
        }
        result = cli("bulk", "ratelimit", "u1:5M/20M,u2:10M/50M", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/bulk/ratelimit",
            json={
                "items": [
                    {"username": "u1", "rate": "5M/20M"},
                    {"username": "u2", "rate": "10M/50M"},
                ]
            },
        )
        assert "1 succeeded" in result.output

    def test_ratelimit_confirm_accept(self, cli, mock_client):
        result = cli("bulk", "ratelimit", "u1:5M/20M", input="y\n")
        assert result.exit_code == 0
        mock_client["post"].assert_called_once()

    def test_ratelimit_confirm_abort(self, cli, mock_client):
        result = cli("bulk", "ratelimit", "u1:5M/20M", input="n\n")
        assert result.exit_code != 0
        mock_client["post"].assert_not_called()

    def test_ratelimit_bad_format(self, cli, mock_client):
        result = cli("bulk", "ratelimit", "badformat")
        assert result.exit_code != 0

    def test_shaper_restore(self, cli, mock_client):
        mock_client["post"].return_value = {
            "operation": "shaper-restore",
            "total": 1,
            "succeeded": 1,
            "failed": 0,
            "results": [{"target": "user1", "success": True, "error": None}],
        }
        result = cli("bulk", "shaper-restore", "user1")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with(
            "/api/v1/bulk/shaper-restore",
            json={"usernames": ["user1"]},
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Playbook (v0.3.1)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPlaybookCommands:
    def test_list(self, cli, mock_client):
        mock_client["get"].return_value = {
            "count": 3,
            "playbooks": [
                {
                    "name": "health-check",
                    "description": "Run health checks",
                    "min_role": "viewer",
                },
                {
                    "name": "backup-config",
                    "description": "Backup config",
                    "min_role": "admin",
                },
                {
                    "name": "safe-restart",
                    "description": "Safe restart",
                    "min_role": "admin",
                },
            ],
        }
        result = cli("playbook", "list")
        assert result.exit_code == 0
        mock_client["get"].assert_called_with("/api/v1/playbooks")

    def test_list_non_dict(self, cli, mock_client):
        mock_client["get"].return_value = [{"name": "health-check"}]
        result = cli("playbook", "list")
        assert result.exit_code == 0

    def test_run(self, cli, mock_client):
        mock_client["post"].return_value = {
            "playbook": "health-check",
            "success": True,
            "steps": [
                {
                    "name": "check_service",
                    "success": True,
                    "output": "running",
                    "error": None,
                },
                {
                    "name": "check_sessions",
                    "success": True,
                    "output": "42 active",
                    "error": None,
                },
            ],
        }
        result = cli("playbook", "run", "health-check", "--force")
        assert result.exit_code == 0
        mock_client["post"].assert_called_with("/api/v1/playbooks/health-check/run")

    def test_run_confirm_abort(self, cli, mock_client):
        result = cli("playbook", "run", "safe-restart", input="n\n")
        assert result.exit_code != 0

    def test_run_failure(self, cli, mock_client):
        mock_client["post"].return_value = {
            "playbook": "safe-restart",
            "success": False,
            "steps": [
                {"name": "drain", "success": True, "output": "drained", "error": None},
                {
                    "name": "restart",
                    "success": False,
                    "output": None,
                    "error": "timeout",
                },
            ],
        }
        result = cli("playbook", "run", "safe-restart", "--force")
        assert result.exit_code == 0
        assert "✗" in result.output
