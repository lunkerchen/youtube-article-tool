import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.main import (
    _dedup_consecutive,
    _parse_subtitle,
    _pick_best_subtitle,
    clean_json_sub,
    clean_srt,
    clean_vtt,
    delete_history_item,
    get_best_thumbnail,
    load_history,
    run_with_retry,
    save_history,
)


# ──────────────────────────────────────────────
# 1. _dedup_consecutive
# ──────────────────────────────────────────────
class TestDedupConsecutive:
    def test_empty_list(self):
        assert _dedup_consecutive([]) == ""

    def test_single_element(self):
        assert _dedup_consecutive(["hello"]) == "hello"

    def test_consecutive_duplicates_collapsed(self):
        lines = ["a", "a", "b", "b", "b", "c"]
        assert _dedup_consecutive(lines) == "a b c"

    def test_non_consecutive_duplicates_kept(self):
        lines = ["a", "b", "a", "c", "a"]
        assert _dedup_consecutive(lines) == "a b a c a"

    def test_all_same(self):
        assert _dedup_consecutive(["x", "x", "x"]) == "x"

    def test_empty_strings_kept_when_separated(self):
        lines = ["a", "", "a"]
        assert _dedup_consecutive(lines) == "a  a"


# ──────────────────────────────────────────────
# 2. clean_vtt
# ──────────────────────────────────────────────
class TestCleanVtt:
    def test_strips_header_and_timestamps(self, tmp_path):
        vtt = tmp_path / "test.vtt"
        vtt.write_text(
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "Hello world\n\n"
            "00:00:05.000 --> 00:00:08.000\n"
            "Second line\n",
            encoding="utf-8",
        )
        result = clean_vtt(str(vtt))
        assert result == "Hello world Second line"

    def test_strips_html_tags(self, tmp_path):
        vtt = tmp_path / "tags.vtt"
        vtt.write_text(
            "WEBVTT\n\n"
            "<c.yellow>Bold text</c>\n\n"
            "<i>Italic</i>\n",
            encoding="utf-8",
        )
        result = clean_vtt(str(vtt))
        assert result == "Bold text Italic"

    def test_dedup_consecutive_lines(self, tmp_path):
        vtt = tmp_path / "dedup.vtt"
        vtt.write_text(
            "WEBVTT\n\n"
            "00:00:00.000 --> 00:00:03.000\n"
            "Same line\n\n"
            "00:00:03.000 --> 00:00:06.000\n"
            "Same line\n\n"
            "00:00:06.000 --> 00:00:09.000\n"
            "Different\n",
            encoding="utf-8",
        )
        result = clean_vtt(str(vtt))
        assert result == "Same line Different"

    def test_empty_vtt(self, tmp_path):
        vtt = tmp_path / "empty.vtt"
        vtt.write_text("WEBVTT\n\n", encoding="utf-8")
        result = clean_vtt(str(vtt))
        assert result == ""


# ──────────────────────────────────────────────
# 3. clean_srt
# ──────────────────────────────────────────────
class TestCleanSrt:
    def test_strips_sequence_and_timestamps(self, tmp_path):
        srt = tmp_path / "test.srt"
        srt.write_text(
            "1\n"
            "00:00:01,000 --> 00:00:04,000\n"
            "Hello world\n\n"
            "2\n"
            "00:00:05,000 --> 00:00:08,000\n"
            "Second line\n",
            encoding="utf-8",
        )
        result = clean_srt(str(srt))
        assert result == "Hello world Second line"

    def test_strips_blank_lines(self, tmp_path):
        srt = tmp_path / "blanks.srt"
        srt.write_text(
            "1\n"
            "00:00:00,000 --> 00:00:02,000\n"
            "Line one\n"
            "\n"
            "2\n"
            "00:00:03,000 --> 00:00:05,000\n"
            "Line two\n",
            encoding="utf-8",
        )
        result = clean_srt(str(srt))
        assert result == "Line one Line two"

    def test_dedup(self, tmp_path):
        srt = tmp_path / "dedup.srt"
        srt.write_text(
            "1\n"
            "00:00:00,000 --> 00:00:02,000\n"
            "Repeated\n\n"
            "2\n"
            "00:00:03,000 --> 00:00:05,000\n"
            "Repeated\n\n"
            "3\n"
            "00:00:06,000 --> 00:00:08,000\n"
            "Different\n",
            encoding="utf-8",
        )
        result = clean_srt(str(srt))
        assert result == "Repeated Different"

    def test_empty_srt(self, tmp_path):
        srt = tmp_path / "empty.srt"
        srt.write_text("", encoding="utf-8")
        result = clean_srt(str(srt))
        assert result == ""


# ──────────────────────────────────────────────
# 4. clean_json_sub
# ──────────────────────────────────────────────
class TestCleanJsonSub:
    def test_extracts_utf8_from_events(self, tmp_path):
        sub = tmp_path / "test.json"
        data = {
            "events": [
                {"segs": [{"utf8": "Hello "}, {"utf8": "world"}]},
                {"segs": [{"utf8": "foo"}, {"utf8": " bar"}]},
            ]
        }
        sub.write_text(json.dumps(data), encoding="utf-8")
        result = clean_json_sub(str(sub))
        assert result == "Hello world foo bar"

    def test_skips_empty_segs(self, tmp_path):
        sub = tmp_path / "empty_segs.json"
        data = {
            "events": [
                {"segs": [{"utf8": ""}, {"utf8": "real"}]},
                {"segs": []},
                {"segs": [{"utf8": "  "}]},
            ]
        }
        sub.write_text(json.dumps(data), encoding="utf-8")
        result = clean_json_sub(str(sub))
        assert result == "real"

    def test_no_events(self, tmp_path):
        sub = tmp_path / "no_events.json"
        sub.write_text(json.dumps({"events": []}), encoding="utf-8")
        result = clean_json_sub(str(sub))
        assert result == ""

    def test_event_without_segs(self, tmp_path):
        sub = tmp_path / "no_segs.json"
        data = {"events": [{"segs": []}, {}]}
        sub.write_text(json.dumps(data), encoding="utf-8")
        result = clean_json_sub(str(sub))
        assert result == ""


# ──────────────────────────────────────────────
# 5. load_history / save_history / delete_history_item
# ──────────────────────────────────────────────
class TestHistory:
    @pytest.fixture(autouse=True)
    def _patch_history_file(self, tmp_path, monkeypatch):
        self.history_file = str(tmp_path / "history.json")
        monkeypatch.setattr("app.main.HISTORY_FILE", self.history_file)

    def _make_item(self, url="https://example.com/1", title="Title 1"):
        return {"url": url, "title": title}

    def test_load_returns_empty_when_no_file(self):
        assert load_history() == []

    def test_load_returns_list_from_file(self):
        items = [self._make_item()]
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False)
        assert load_history() == items

    def test_load_returns_empty_on_corrupt_file(self):
        Path(self.history_file).write_text("not json {{{")
        assert load_history() == []

    def test_save_and_load(self):
        item = self._make_item()
        save_history(item)
        assert load_history() == [item]

    def test_save_dedup_by_url(self):
        save_history(self._make_item(title="v1"))
        save_history(self._make_item(title="v2"))
        history = load_history()
        assert len(history) == 1
        assert history[0]["title"] == "v2"

    def test_save_inserts_at_front(self):
        save_history(self._make_item(url="https://example.com/a"))
        save_history(self._make_item(url="https://example.com/b"))
        history = load_history()
        assert history[0]["url"] == "https://example.com/b"
        assert history[1]["url"] == "https://example.com/a"

    def test_save_max_50_items(self):
        for i in range(55):
            save_history(self._make_item(url=f"https://example.com/{i}"))
        history = load_history()
        assert len(history) == 50

    def test_delete_history_item(self):
        save_history(self._make_item(url="https://example.com/keep"))
        save_history(self._make_item(url="https://example.com/remove"))
        delete_history_item("https://example.com/remove")
        history = load_history()
        assert len(history) == 1
        assert history[0]["url"] == "https://example.com/keep"

    def test_delete_nonexistent_url_is_noop(self):
        save_history(self._make_item())
        delete_history_item("https://example.com/nope")
        assert len(load_history()) == 1


# ──────────────────────────────────────────────
# 6. get_best_thumbnail
# ──────────────────────────────────────────────
class TestGetBestThumbnail:
    def test_returns_last_thumbnail_url(self):
        meta = {
            "thumbnails": [
                {"url": "https://example.com/thumb1.jpg"},
                {"url": "https://example.com/thumb2.jpg"},
            ]
        }
        assert get_best_thumbnail(meta) == "https://example.com/thumb2.jpg"

    def test_falls_back_to_img_youtube(self):
        meta = {"id": "dQw4w9WgXcQ", "thumbnails": []}
        result = get_best_thumbnail(meta)
        assert result == "https://img.youtube.com/vi/dQw4w9WgXcQ/sddefault.jpg"

    def test_empty_thumbnails_uses_id(self):
        meta = {"id": "abc123"}
        result = get_best_thumbnail(meta)
        assert result == "https://img.youtube.com/vi/abc123/sddefault.jpg"

    def test_no_id_returns_empty(self):
        meta = {}
        assert get_best_thumbnail(meta) == ""

    def test_no_thumbnails_key_and_no_id(self):
        assert get_best_thumbnail({"title": "something"}) == ""

    def test_single_thumbnail(self):
        meta = {"thumbnails": [{"url": "https://example.com/one.jpg"}]}
        assert get_best_thumbnail(meta) == "https://example.com/one.jpg"


# ──────────────────────────────────────────────
# 7. run_with_retry
# ──────────────────────────────────────────────
class TestRunWithRetry:
    @patch("app.main.subprocess.run")
    def test_success_first_try(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout=b"ok", stderr=b"")
        result, err = run_with_retry(["echo", "hi"])
        assert result.returncode == 0
        assert err is None
        assert mock_run.call_count == 1

    @patch("app.main.time.sleep")
    @patch("app.main.subprocess.run")
    def test_retries_on_broken_pipe(self, mock_run, mock_sleep):
        mock_run.side_effect = [
            BrokenPipeError("pipe broke"),
            MagicMock(returncode=0, stdout=b"ok", stderr=b""),
        ]
        result, err = run_with_retry(["cmd"], retries=2)
        assert result is not None
        assert err is None
        assert mock_run.call_count == 2

    @patch("app.main.time.sleep")
    @patch("app.main.subprocess.run")
    def test_exhausts_retries(self, mock_run, mock_sleep):
        mock_run.side_effect = BrokenPipeError("pipe broke")
        result, err = run_with_retry(["cmd"], retries=1)
        assert result is None
        assert "BrokenPipeError" in err

    @patch("app.main.subprocess.run")
    def test_timeout_returns_error(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="cmd", timeout=5)
        result, err = run_with_retry(["cmd"], timeout=5)
        assert result is None
        assert err == "subprocess 逾時"

    @patch("app.main.subprocess.run")
    def test_generic_exception(self, mock_run):
        mock_run.side_effect = RuntimeError("boom")
        result, err = run_with_retry(["cmd"])
        assert result is None
        assert "boom" in err


# ──────────────────────────────────────────────
# 8. _pick_best_subtitle
# ──────────────────────────────────────────────
class TestPickBestSubtitle:
    def test_picks_english_when_available(self):
        files = ["/subs/fr_123.vtt", "/subs/en_456.vtt", "/subs/de_789.vtt"]
        assert _pick_best_subtitle(files) == "/subs/en_456.vtt"

    def test_picks_first_priority_match(self):
        files = ["/subs/ja_001.srt", "/subs/ko_002.srt"]
        assert _pick_best_subtitle(files) == "/subs/ja_001.srt"

    def test_falls_back_to_first_file(self):
        files = ["/subs/fr_001.vtt", "/subs/de_002.vtt"]
        assert _pick_best_subtitle(files) == "/subs/fr_001.vtt"

    def test_single_file(self):
        assert _pick_best_subtitle(["only.vtt"]) == "only.vtt"

    def test_prefers_zh_over_en_when_en_missing(self):
        files = ["/subs/ja_001.vtt", "/subs/zh_002.vtt"]
        assert _pick_best_subtitle(files) == "/subs/zh_002.vtt"

    def test_auto_subtitle_en_matches_french_containing_en(self):
        files = ["/subs/video.french_auto.vtt", "/subs/video.english.vtt"]
        assert _pick_best_subtitle(files) == "/subs/video.french_auto.vtt"

    def test_en_exact_match_wins(self):
        files = ["/subs/video.de_001.vtt", "/subs/video.en_002.vtt"]
        assert _pick_best_subtitle(files) == "/subs/video.en_002.vtt"


# ──────────────────────────────────────────────
# 9. _parse_subtitle
# ──────────────────────────────────────────────
class TestParseSubtitle:
    def test_routes_to_vtt_parser(self, tmp_path):
        vtt = tmp_path / "sub.vtt"
        vtt.write_text(
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "VTT content\n",
            encoding="utf-8",
        )
        result = _parse_subtitle(str(vtt))
        assert result == "VTT content"

    def test_routes_to_srt_parser(self, tmp_path):
        srt = tmp_path / "sub.srt"
        srt.write_text(
            "1\n"
            "00:00:01,000 --> 00:00:03,000\n"
            "SRT content\n",
            encoding="utf-8",
        )
        result = _parse_subtitle(str(srt))
        assert result == "SRT content"

    def test_routes_to_json_parser(self, tmp_path):
        sub = tmp_path / "sub.json"
        data = {"events": [{"segs": [{"utf8": "JSON content"}]}]}
        sub.write_text(json.dumps(data), encoding="utf-8")
        result = _parse_subtitle(str(sub))
        assert result == "JSON content"

    def test_falls_back_to_plain_text(self, tmp_path):
        unknown = tmp_path / "sub.srv1"
        unknown.write_text("plain text here", encoding="utf-8")
        result = _parse_subtitle(str(unknown))
        assert result == "plain text here"
