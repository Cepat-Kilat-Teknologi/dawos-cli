"""Tests for commands/node.py — multi-node group management and execution."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from dawos_cli.multi import MultiResult, NodeResult

# ---------------------------------------------------------------------------
# group-add
# ---------------------------------------------------------------------------


class TestGroupAdd:
    """Tests for 'dawos node group-add'."""

    def test_add_group_success(self, cli, tmp_config):
        """Create a group with valid profiles."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_profile("bng2", "http://bng2:8470", "key2")

        result = cli(
            "node", "group-add", "core", "--profiles", "bng1", "--profiles", "bng2"
        )
        assert result.exit_code == 0
        assert "core" in result.output
        assert "2 profile" in result.output

    def test_add_group_unknown_profile(self, cli, tmp_config):
        """Reject group with non-existent profiles."""
        result = cli("node", "group-add", "bad", "--profiles", "nonexistent")
        assert result.exit_code == 1
        assert "Unknown" in result.output

    def test_add_group_overwrite(self, cli, tmp_config):
        """Overwriting an existing group succeeds."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_profile("bng2", "http://bng2:8470", "key2")

        cli("node", "group-add", "core", "--profiles", "bng1")
        result = cli(
            "node", "group-add", "core", "--profiles", "bng1", "--profiles", "bng2"
        )
        assert result.exit_code == 0
        assert "2 profile" in result.output


# ---------------------------------------------------------------------------
# group-remove
# ---------------------------------------------------------------------------


class TestGroupRemove:
    """Tests for 'dawos node group-remove'."""

    def test_remove_existing_group(self, cli, tmp_config):
        """Remove a group that exists."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        result = cli("node", "group-remove", "core")
        assert result.exit_code == 0
        assert "removed" in result.output.lower()

    def test_remove_nonexistent_group(self, cli, tmp_config):
        """Removing a group that doesn't exist fails."""
        result = cli("node", "group-remove", "nope")
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


# ---------------------------------------------------------------------------
# group-list
# ---------------------------------------------------------------------------


class TestGroupList:
    """Tests for 'dawos node group-list'."""

    def test_list_empty(self, cli, tmp_config):
        """No groups shows a warning."""
        result = cli("node", "group-list")
        assert result.exit_code == 0
        assert "No groups" in result.output

    def test_list_with_groups(self, cli, tmp_config):
        """Groups are listed with member count."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_profile("bng2", "http://bng2:8470", "key2")
        config.add_group("core", ["bng1", "bng2"])

        result = cli("node", "group-list")
        assert result.exit_code == 0
        assert "core" in result.output
        assert "2" in result.output


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


class TestNodeStatus:
    """Tests for 'dawos node status'."""

    def test_status_success(self, cli, tmp_config):
        """Status check shows healthy nodes."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        mock_result = MultiResult(
            total=1,
            succeeded=1,
            failed=0,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=True,
                    status_code=200,
                    data={"status": "ok", "version": "0.1.0", "node_name": "bng1"},
                )
            ],
        )
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli("node", "status", "core")

        assert result.exit_code == 0
        assert "bng1" in result.output
        assert "healthy" in result.output.lower()

    def test_status_group_not_found(self, cli, tmp_config):
        """Status check on unknown group fails."""
        result = cli("node", "status", "missing")
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_status_empty_group(self, cli, tmp_config):
        """Status check on empty group shows warning."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("empty", [])
        # Need to manually write empty group since add_group validates
        import dawos_cli.config as cfg

        data = cfg._load()
        data["groups"]["empty"] = []
        cfg._save(data)

        result = cli("node", "status", "empty")
        assert result.exit_code == 0
        assert "no profiles" in result.output.lower()

    def test_status_with_failed_node(self, cli, tmp_config):
        """Status check shows failed nodes."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        mock_result = MultiResult(
            total=1,
            succeeded=0,
            failed=1,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=False,
                    error="Connection refused",
                )
            ],
        )
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli("node", "status", "core")

        assert result.exit_code == 0
        assert "Failed" in result.output


# ---------------------------------------------------------------------------
# exec
# ---------------------------------------------------------------------------


class TestNodeExec:
    """Tests for 'dawos node exec'."""

    def test_exec_get(self, cli, tmp_config):
        """Execute GET request on group."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        mock_result = MultiResult(
            total=1,
            succeeded=1,
            failed=0,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=True,
                    status_code=200,
                    data={"sessions": 42},
                )
            ],
        )
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli("node", "exec", "core", "GET", "/api/v1/sessions")

        assert result.exit_code == 0
        assert "bng1" in result.output
        assert "200" in result.output

    def test_exec_post_with_body(self, cli, tmp_config):
        """Execute POST request with JSON body."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        mock_result = MultiResult(
            total=1,
            succeeded=1,
            failed=0,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=True,
                    status_code=200,
                    data={"success": True},
                )
            ],
        )
        body = json.dumps({"username": "user1"})
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli(
                "node",
                "exec",
                "core",
                "POST",
                "/api/v1/something",
                "--body",
                body,
            )

        assert result.exit_code == 0

    def test_exec_invalid_body(self, cli, tmp_config):
        """Invalid JSON body is rejected."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        result = cli("node", "exec", "core", "POST", "/test", "--body", "not-json")
        assert result.exit_code == 1
        assert "Invalid JSON" in result.output

    def test_exec_invalid_method(self, cli, tmp_config):
        """Invalid HTTP method is rejected."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        result = cli("node", "exec", "core", "BANANA", "/test")
        assert result.exit_code == 1
        assert "Invalid HTTP method" in result.output

    def test_exec_group_not_found(self, cli, tmp_config):
        """Exec on unknown group fails."""
        result = cli("node", "exec", "missing", "GET", "/health")
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_exec_empty_group(self, cli, tmp_config):
        """Exec on empty group shows warning."""
        import dawos_cli.config as cfg

        data = cfg._load()
        data.setdefault("groups", {})["empty"] = []
        cfg._save(data)

        result = cli("node", "exec", "empty", "GET", "/health")
        assert result.exit_code == 0
        assert "no profiles" in result.output.lower()

    def test_exec_with_failure(self, cli, tmp_config):
        """Exec shows failure details."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        mock_result = MultiResult(
            total=1,
            succeeded=0,
            failed=1,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=False,
                    error="Connection refused",
                )
            ],
        )
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli("node", "exec", "core", "GET", "/health")

        assert result.exit_code == 0
        assert "Failed" in result.output

    def test_exec_long_response_truncated(self, cli, tmp_config):
        """Long responses are truncated in the table."""
        from dawos_cli import config

        config.add_profile("bng1", "http://bng1:8470", "key1")
        config.add_group("core", ["bng1"])

        long_data = {"key": "x" * 200}
        mock_result = MultiResult(
            total=1,
            succeeded=1,
            failed=0,
            results=[
                NodeResult(
                    profile="bng1",
                    url="http://bng1:8470",
                    success=True,
                    status_code=200,
                    data=long_data,
                )
            ],
        )
        with patch("dawos_cli.commands.node.execute_multi", return_value=mock_result):
            result = cli("node", "exec", "core", "GET", "/api/v1/something")

        assert result.exit_code == 0
        assert "..." in result.output


# ---------------------------------------------------------------------------
# Config group functions
# ---------------------------------------------------------------------------


class TestConfigGroups:
    """Tests for config.py group CRUD functions."""

    def test_list_groups_empty(self, tmp_config):
        from dawos_cli import config

        assert config.list_groups() == {}

    def test_add_and_get_group(self, tmp_config):
        from dawos_cli import config

        config.add_profile("a", "http://a:8470", "k")
        config.add_profile("b", "http://b:8470", "k")
        config.add_group("test", ["a", "b"])

        group = config.get_group("test")
        assert group == ["a", "b"]

    def test_get_group_not_found(self, tmp_config):
        from dawos_cli import config

        assert config.get_group("nope") is None

    def test_remove_group(self, tmp_config):
        from dawos_cli import config

        config.add_profile("a", "http://a:8470", "k")
        config.add_group("test", ["a"])
        assert config.remove_group("test") is True
        assert config.get_group("test") is None

    def test_remove_group_not_found(self, tmp_config):
        from dawos_cli import config

        assert config.remove_group("nope") is False

    def test_add_group_unknown_profile_raises(self, tmp_config):
        from dawos_cli import config

        with pytest.raises(ValueError, match="Unknown profiles"):
            config.add_group("bad", ["nonexistent"])

    def test_list_groups_with_data(self, tmp_config):
        from dawos_cli import config

        config.add_profile("a", "http://a:8470", "k")
        config.add_group("g1", ["a"])
        groups = config.list_groups()
        assert "g1" in groups
        assert groups["g1"] == ["a"]
