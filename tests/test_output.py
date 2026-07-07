"""Tests for dawos_cli.output module."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest
from rich.console import Console

from dawos_cli import output, state


@pytest.fixture
def capture():
    """Capture Rich console output to a string."""
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    with (
        patch.object(output, "console", console),
        patch.object(
            output,
            "err_console",
            Console(file=buf, stderr=True, force_terminal=True, width=120),
        ),
    ):
        yield buf


class TestPrimitives:
    def test_print_json(self, capture):
        output.print_json({"key": "value"})
        text = capture.getvalue()
        assert "key" in text
        assert "value" in text

    def test_print_raw(self, capture):
        output.print_raw("hello world")
        assert "hello world" in capture.getvalue()

    def test_success(self, capture):
        output.success("it worked")
        assert "it worked" in capture.getvalue()

    def test_warning(self, capture):
        output.warning("be careful")
        assert "be careful" in capture.getvalue()

    def test_error(self, capture):
        output.error("something broke")
        assert "something broke" in capture.getvalue()

    def test_info(self, capture):
        output.info("fyi")
        assert "fyi" in capture.getvalue()


class TestTable:
    def test_table_renders(self, capture):
        rows = [{"name": "pool1", "size": 256}, {"name": "pool2", "size": 512}]
        output.table(rows, ["name", "size"], title="Pools")
        text = capture.getvalue()
        assert "pool1" in text
        assert "pool2" in text

    def test_table_json_mode(self, capture):
        state.current.json_output = True
        rows = [{"name": "pool1"}]
        output.table(rows, ["name"])
        text = capture.getvalue()
        assert "pool1" in text

    def test_table_empty(self, capture):
        output.table([], ["name", "size"], title="Empty")
        text = capture.getvalue()
        assert "—" in text

    def test_table_col_labels(self, capture):
        rows = [{"name": "test"}]
        output.table(rows, ["name"], col_labels={"name": "Node"})
        text = capture.getvalue()
        assert "Node" in text

    def test_table_col_styles(self, capture):
        rows = [{"name": "test"}]
        output.table(rows, ["name"], col_styles={"name": "bold"})
        text = capture.getvalue()
        assert "test" in text


class TestDetail:
    def test_detail_renders(self, capture):
        output.detail({"hostname": "bng1", "uptime": "5 days"}, title="Info")
        text = capture.getvalue()
        assert "bng1" in text
        assert "5 days" in text

    def test_detail_json_mode(self, capture):
        state.current.json_output = True
        output.detail({"hostname": "bng1"})
        text = capture.getvalue()
        assert "bng1" in text


class TestKvtable:
    def test_kvtable_renders(self, capture):
        output.kvtable({"cpu": "10%", "mem": "50%"}, title="Resources")
        text = capture.getvalue()
        assert "10%" in text
        assert "50%" in text

    def test_kvtable_json_mode(self, capture):
        state.current.json_output = True
        output.kvtable({"cpu": "10%"})
        text = capture.getvalue()
        assert "10%" in text


class TestResponse:
    def test_response_dict(self, capture):
        output.response({"key": "val"}, title="Test")
        text = capture.getvalue()
        assert "val" in text

    def test_response_list(self, capture):
        output.response([{"a": 1, "b": 2}], title="List")
        text = capture.getvalue()
        assert "1" in text

    def test_response_other(self, capture):
        output.response("plain text")
        assert "plain text" in capture.getvalue()

    def test_response_json_mode(self, capture):
        state.current.json_output = True
        output.response({"key": "val"})
        text = capture.getvalue()
        assert "val" in text

    def test_response_empty_list(self, capture):
        output.response([], title="Empty")
        # Empty list is not dict, not list-of-dicts — printed as-is
        capture.getvalue()  # no crash


class TestCsvFormat:
    def test_table_csv(self, capture):
        state.current.output_format = "csv"
        rows = [{"name": "pool1", "size": 256}, {"name": "pool2", "size": 512}]
        output.table(rows, ["name", "size"])
        # CSV goes to sys.stdout, not Rich console — check it didn't crash
        # and Rich console buffer is empty (output went to stdout)
        assert capture.getvalue() == ""

    def test_detail_csv(self, capture):
        state.current.output_format = "csv"
        output.detail({"hostname": "bng1", "uptime": "5 days"})
        assert capture.getvalue() == ""  # went to stdout

    def test_response_csv_dict(self, capture):
        state.current.output_format = "csv"
        output.response({"k": "v"})
        assert capture.getvalue() == ""

    def test_csv_empty_data_fallback(self, capture):
        """CSV with non-tabular data — not dict/list, falls through to console."""
        state.current.output_format = "csv"
        output.response("plain text")
        # "plain text" is not dict/list, _emit returns False for csv,
        # response() falls through to console.print(data)
        assert "plain text" in capture.getvalue()


class TestYamlFormat:
    def test_table_yaml(self, capture):
        state.current.output_format = "yaml"
        rows = [{"name": "pool1"}]
        output.table(rows, ["name"])
        # YAML goes to stdout (or falls back to JSON with warning)
        # Either way, _emit returns True so Rich table is NOT rendered
        text = capture.getvalue()
        # If PyYAML is not installed, a warning is printed to err_console
        # which is also captured — that's fine, just verify no crash
        assert "pool1" not in text or "PyYAML" in text

    def test_detail_yaml(self, capture):
        state.current.output_format = "yaml"
        output.detail({"hostname": "bng1"})
        text = capture.getvalue()
        assert "Hostname" not in text  # Rich panel NOT rendered

    def test_yaml_fallback_no_pyyaml(self, capture):
        """When PyYAML is not installed, falls back to JSON."""
        state.current.output_format = "yaml"
        with patch.dict("sys.modules", {"yaml": None}):
            output.table([{"name": "pool1"}], ["name"])
            # Should not crash — falls back to JSON
