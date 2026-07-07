"""Tests for dawos_cli.dashboard module."""

from __future__ import annotations

from unittest.mock import patch

from dawos_cli import dashboard


class TestFmtBytes:
    def test_none(self):
        assert dashboard._fmt_bytes(None) == "—"

    def test_dash(self):
        assert dashboard._fmt_bytes("—") == "—"

    def test_empty(self):
        assert dashboard._fmt_bytes("") == "—"

    def test_zero(self):
        assert "0" in dashboard._fmt_bytes(0)

    def test_bytes(self):
        assert "B" in dashboard._fmt_bytes(500)

    def test_kilobytes(self):
        result = dashboard._fmt_bytes(2048)
        assert "KB" in result

    def test_megabytes(self):
        result = dashboard._fmt_bytes(5 * 1024 * 1024)
        assert "MB" in result

    def test_gigabytes(self):
        result = dashboard._fmt_bytes(3 * 1024**3)
        assert "GB" in result

    def test_terabytes(self):
        result = dashboard._fmt_bytes(2 * 1024**4)
        assert "TB" in result

    def test_petabytes(self):
        result = dashboard._fmt_bytes(2 * 1024**5)
        assert "PB" in result

    def test_non_numeric(self):
        assert dashboard._fmt_bytes("abc") == "abc"


class TestFetchSafe:
    def test_returns_dict(self, mock_client):
        mock_client["get"].return_value = {"cpu": 10}
        assert dashboard._fetch_safe("/api/v1/test") == {"cpu": 10}

    def test_returns_empty_on_error(self, mock_client):
        mock_client["get"].side_effect = Exception("fail")
        assert dashboard._fetch_safe("/api/v1/test") == {}

    def test_returns_empty_on_non_dict(self, mock_client):
        mock_client["get"].return_value = [1, 2, 3]
        assert dashboard._fetch_safe("/api/v1/test") == {}

    def test_returns_empty_on_system_exit(self, mock_client):
        mock_client["get"].side_effect = SystemExit(1)
        assert dashboard._fetch_safe("/api/v1/test") == {}


class TestFetchSessionsSafe:
    def test_returns_sessions(self, mock_client):
        mock_client["get"].return_value = {"sessions": [{"username": "u1"}]}
        assert dashboard._fetch_sessions_safe() == [{"username": "u1"}]

    def test_returns_list_directly(self, mock_client):
        mock_client["get"].return_value = [{"username": "u1"}]
        assert dashboard._fetch_sessions_safe() == [{"username": "u1"}]

    def test_returns_empty_on_error(self, mock_client):
        mock_client["get"].side_effect = Exception("fail")
        assert dashboard._fetch_sessions_safe() == []


class TestBuildPanels:
    def test_stat_panel(self):
        panel = dashboard._build_stat_panel({"active_sessions": 42, "uptime": "1h"})
        assert panel is not None

    def test_stat_panel_alternate_keys(self):
        panel = dashboard._build_stat_panel(
            {
                "sessions": 42,
                "starting": 1,
                "active": 40,
                "finishing": 1,
                "uptime_seconds": 3600,
                "total_sessions": 100,
                "total_bytes_in": 1024,
                "total_bytes_out": 2048,
            }
        )
        assert panel is not None

    def test_resource_panel(self):
        panel = dashboard._build_resource_panel(
            {
                "cpu": {"usage_percent": 10, "cores": 4},
                "memory": {"used_percent": 50, "total": 8 * 1024**3},
                "disk": {"used_percent": 30},
                "load_average": [1.0, 0.5, 0.3],
            }
        )
        assert panel is not None

    def test_resource_panel_alt_keys(self):
        panel = dashboard._build_resource_panel(
            {
                "cpu": {"percent": 10},
                "memory": {"percent": 50},
                "load": "1.0",
            }
        )
        assert panel is not None

    def test_resource_panel_scalar_cpu(self):
        panel = dashboard._build_resource_panel({"cpu": "10%", "memory": "50%"})
        assert panel is not None

    def test_sessions_table(self):
        panel = dashboard._build_sessions_table(
            [
                {
                    "username": "u1",
                    "ip": "10.0.0.1",
                    "mac": "aa:bb",
                    "interface": "eth0",
                    "uptime": "1h",
                    "rx_bytes": 1024,
                    "tx_bytes": 2048,
                    "rate_limit": "10M/20M",
                }
            ]
        )
        assert panel is not None

    def test_sessions_table_alt_keys(self):
        panel = dashboard._build_sessions_table(
            [
                {
                    "username": "u1",
                    "ip_address": "10.0.0.1",
                    "calling_station_id": "aa:bb",
                    "ifname": "eth0",
                    "uptime": "1h",
                    "bytes_in": 1024,
                    "bytes_out": 2048,
                    "rate": "10M",
                }
            ]
        )
        assert panel is not None

    def test_sessions_table_empty(self):
        panel = dashboard._build_sessions_table([])
        assert panel is not None

    def test_header(self):
        header = dashboard._build_header("prod", "http://bng:8470")
        assert "DAWOS" in header.plain
        assert "prod" in header.plain


class TestRunDashboard:
    def test_run_dashboard_keyboard_interrupt(self, mock_client):
        """Test run_dashboard exits cleanly on KeyboardInterrupt."""
        mock_client["get"].return_value = {"active_sessions": 0}
        with (
            patch("dawos_cli.dashboard.Live") as mock_live,
            patch("dawos_cli.dashboard.time") as mock_time,
        ):
            mock_time.sleep.side_effect = KeyboardInterrupt()
            dashboard.run_dashboard(interval=1.0)
            mock_live.assert_called_once()

    def test_run_dashboard_renders_layout(self, mock_client):
        """Test run_dashboard builds and updates layout."""
        mock_client["get"].return_value = {"active_sessions": 5}
        call_count = 0

        def _sleep_then_interrupt(interval):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                raise KeyboardInterrupt()

        with (
            patch("dawos_cli.dashboard.Live") as mock_live,
            patch("dawos_cli.dashboard.time") as mock_time,
        ):
            mock_time.sleep.side_effect = _sleep_then_interrupt
            ctx = mock_live.return_value.__enter__.return_value
            dashboard.run_dashboard(interval=0.1)
            assert ctx.update.called

    def test_dashboard_top_cmd(self, mock_client):
        """Test the dashboard top_cmd typer command."""
        with patch("dawos_cli.dashboard.run_dashboard") as mock_rd:
            from dawos_cli.dashboard import top_cmd

            top_cmd(interval=2.0)
            mock_rd.assert_called_once_with(interval=2.0)
