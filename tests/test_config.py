"""Tests for dawos_cli.config module."""

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
