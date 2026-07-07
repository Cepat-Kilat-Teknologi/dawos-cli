"""Tests for dawos_cli.state module."""

from dawos_cli.state import AppState, current


class TestAppState:
    def test_defaults(self):
        s = AppState()
        assert s.profile_name == ""
        assert s.base_url == ""
        assert s.api_key == ""
        assert s.json_output is False
        assert s.verbose is False
        assert s.timeout == 30.0

    def test_singleton_exists(self):
        assert isinstance(current, AppState)

    def test_mutable(self):
        s = AppState()
        s.profile_name = "prod"
        s.base_url = "http://10.0.0.1:8470"
        s.api_key = "secret"
        s.json_output = True
        s.verbose = True
        s.timeout = 60.0
        assert s.profile_name == "prod"
        assert s.base_url == "http://10.0.0.1:8470"
        assert s.api_key == "secret"
        assert s.json_output is True
        assert s.verbose is True
        assert s.timeout == 60.0
