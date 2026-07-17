"""Tests for dawos_cli.config module."""

from __future__ import annotations

import stat
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from dawos_cli import config


class TestConfig:
    def test_list_profiles_empty(self, tmp_config):
        assert config.list_profiles() == {}

    def test_add_and_list(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1", "BNG Node 1")
        profiles = config.list_profiles()
        assert "bng1" in profiles
        assert profiles["bng1"]["url"] == "http://10.0.0.1:8470"
        assert profiles["bng1"]["api_key"] == "key1"
        assert profiles["bng1"]["display_name"] == "BNG Node 1"

    def test_add_auto_activates_first(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        assert config.get_active_name() == "bng1"

    def test_add_strips_trailing_slash(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470/", "key1")
        p = config.get_profile("bng1")
        assert p["url"] == "http://10.0.0.1:8470"

    def test_add_default_display_name(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        p = config.get_profile("bng1")
        assert p["display_name"] == "bng1"

    def test_get_profile_by_name(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        p = config.get_profile("bng2")
        assert p["url"] == "http://10.0.0.2:8470"

    def test_get_profile_active(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        p = config.get_profile()  # no name = active
        assert p["url"] == "http://10.0.0.1:8470"

    def test_get_profile_nonexistent(self, tmp_config):
        assert config.get_profile("nope") is None

    def test_get_profile_no_active(self, tmp_config):
        assert config.get_profile() is None

    def test_remove_profile(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        assert config.remove_profile("bng1") is True
        assert config.list_profiles() == {}

    def test_remove_nonexistent(self, tmp_config):
        assert config.remove_profile("nope") is False

    def test_remove_active_switches(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        config.use_profile("bng1")
        config.remove_profile("bng1")
        assert config.get_active_name() == "bng2"

    def test_remove_last_clears_active(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.remove_profile("bng1")
        assert config.get_active_name() == ""

    def test_use_profile(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        assert config.use_profile("bng2") is True
        assert config.get_active_name() == "bng2"

    def test_use_nonexistent(self, tmp_config):
        assert config.use_profile("nope") is False

    def test_config_path(self, tmp_config):
        path = config.config_path()
        assert path.name == "config.json"

    def test_overwrite_profile(self, tmp_config):
        config.add_profile("bng1", "http://old:8470", "old_key")
        config.add_profile("bng1", "http://new:8470", "new_key")
        p = config.get_profile("bng1")
        assert p["url"] == "http://new:8470"
        assert p["api_key"] == "new_key"

    def test_second_add_keeps_active(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        # First profile should remain active
        assert config.get_active_name() == "bng1"


class TestLoadErrorHandling:
    """DC-M02: corrupt or unreadable config exits cleanly, no traceback."""

    def test_corrupt_json_exits_cleanly(self, tmp_config, capsys):
        config.CONFIG_FILE.write_text("{corrupt json!!", encoding="utf-8")
        with pytest.raises(typer.Exit) as excinfo:
            config._load()
        assert excinfo.value.exit_code == 1
        err = capsys.readouterr().err
        assert str(config.CONFIG_FILE) in err
        assert "corrupt or unreadable" in err

    def test_corrupt_json_cli_exit_code(self, cli, tmp_config):
        """A CLI command over a corrupt config exits 1 without a traceback."""
        config.CONFIG_FILE.write_text("{corrupt json!!", encoding="utf-8")
        result = cli("profile", "list")
        assert result.exit_code == 1

    def test_unreadable_file_exits_cleanly(self, tmp_config):
        config.CONFIG_FILE.write_text("{}", encoding="utf-8")
        with patch.object(Path, "read_text", side_effect=OSError("denied")):
            with pytest.raises(typer.Exit) as excinfo:
                config._load()
        assert excinfo.value.exit_code == 1


class TestSaveAtomicPermissions:
    """DC-M07: config is written atomically and never world-readable."""

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
    def test_config_dir_mode_is_0700(self, tmp_config):
        """CLI-03: config directory must be 0700 (owner-only)."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        mode = stat.S_IMODE(config.CONFIG_DIR.stat().st_mode)
        assert mode == 0o700

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
    def test_saved_file_mode_is_0600(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        mode = stat.S_IMODE(config.CONFIG_FILE.stat().st_mode)
        assert mode == 0o600

    def test_no_temp_file_left_behind(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        assert not (tmp_config / "config.json.tmp").exists()
        assert config.get_profile("bng1") is not None

    def test_stale_temp_file_is_replaced(self, tmp_config):
        """A leftover temp file from a crashed write does not block saving."""
        stale = tmp_config / "config.json.tmp"
        stale.write_text("stale", encoding="utf-8")
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        assert not stale.exists()
        assert config.get_profile("bng1") is not None

    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
    def test_overwrite_keeps_0600(self, tmp_config):
        """Re-saving over an existing looser-mode file tightens it to 0600."""
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.CONFIG_FILE.chmod(0o644)
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        mode = stat.S_IMODE(config.CONFIG_FILE.stat().st_mode)
        assert mode == 0o600


class TestExportProfiles:
    def test_export_all(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        result = config.export_profiles()
        assert result["dawos_cli_export"] is True
        assert result["version"] == 1
        assert len(result["profiles"]) == 2

    def test_export_single(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        config.add_profile("bng2", "http://10.0.0.2:8470", "key2")
        result = config.export_profiles("bng1")
        assert len(result["profiles"]) == 1
        assert "bng1" in result["profiles"]

    def test_export_nonexistent(self, tmp_config):
        result = config.export_profiles("nope")
        assert result == {}

    def test_export_empty(self, tmp_config):
        result = config.export_profiles()
        assert result["profiles"] == {}


class TestImportProfiles:
    def test_import_merge(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        payload = {
            "dawos_cli_export": True,
            "version": 1,
            "active_profile": "bng2",
            "profiles": {
                "bng2": {"url": "http://10.0.0.2:8470", "api_key": "key2"},
            },
        }
        count = config.import_profiles(payload, merge=True)
        assert count == 1
        assert config.get_profile("bng1") is not None  # preserved
        assert config.get_profile("bng2") is not None  # imported

    def test_import_replace(self, tmp_config):
        config.add_profile("bng1", "http://10.0.0.1:8470", "key1")
        payload = {
            "profiles": {
                "bng2": {"url": "http://10.0.0.2:8470", "api_key": "key2"},
            },
        }
        count = config.import_profiles(payload, merge=False)
        assert count == 1
        assert config.get_profile("bng1") is None  # replaced
        assert config.get_profile("bng2") is not None

    def test_import_empty(self, tmp_config):
        count = config.import_profiles({"profiles": {}})
        assert count == 0

    def test_import_sets_active_profile(self, tmp_config):
        payload = {
            "active_profile": "bng1",
            "profiles": {
                "bng1": {"url": "http://10.0.0.1:8470", "api_key": "key1"},
            },
        }
        config.import_profiles(payload)
        assert config.get_active_name() == "bng1"

    def test_import_fallback_active(self, tmp_config):
        """When no active_profile in payload, pick the first imported."""
        payload = {
            "profiles": {
                "bng1": {"url": "http://10.0.0.1:8470", "api_key": "key1"},
            },
        }
        config.import_profiles(payload)
        assert config.get_active_name() == "bng1"
