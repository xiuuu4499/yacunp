"""Tests for the Save Text node's file-writing helper."""

from __future__ import annotations

import os

from yacunp.comfyui_yacunp.nodes.io.save_text import write_text_file


def test_writes_file_with_prefix_and_extension(tmp_path):
    path, filename = write_text_file(str(tmp_path), "hello", "report", "txt")
    assert filename == "report.txt"
    assert os.path.dirname(path) == str(tmp_path)
    assert open(path, encoding="utf-8").read() == "hello"


def test_json_extension(tmp_path):
    _path, filename = write_text_file(str(tmp_path), "{}", "meta", "json")
    assert filename == "meta.json"


def test_disambiguates_existing_file(tmp_path):
    _p1, f1 = write_text_file(str(tmp_path), "a", "out", "txt")
    _p2, f2 = write_text_file(str(tmp_path), "b", "out", "txt")
    assert f1 == "out.txt"
    assert f2 == "out_001.txt"


def test_sanitizes_path_traversal(tmp_path):
    path, filename = write_text_file(str(tmp_path), "x", "../../etc/passwd", "txt")
    assert os.path.dirname(path) == str(tmp_path)
    assert "/" not in filename
    assert filename.endswith(".txt")


def test_none_text_writes_empty(tmp_path):
    path, _filename = write_text_file(str(tmp_path), None, "empty", "txt")
    assert open(path, encoding="utf-8").read() == ""
