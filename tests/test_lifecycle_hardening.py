from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lifecycle

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "errors" / "catalog.json"
PROFILE_PATH = ROOT / "profiles" / "reference.lifecycle"


class LifecycleHardeningTests(unittest.TestCase):
    catalog: dict[str, lifecycle.CatalogEntry]

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = lifecycle.load_catalog(CATALOG_PATH)

    def test_validate_and_audit_reject_symlink_and_directory_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            link_path = tmp_dir / "linked.lifecycle"
            link_path.symlink_to(PROFILE_PATH)

            report = lifecycle.validate_path(link_path, self.catalog)
            self.assertFalse(report.valid)
            self.assertEqual([d.code for d in report.diagnostics], ["LFC-IO-001"])

            dir_report = lifecycle.validate_path(tmp_dir, self.catalog)
            self.assertFalse(dir_report.valid)
            self.assertEqual([d.code for d in dir_report.diagnostics], ["LFC-IO-001"])

            audit = lifecycle.audit_path(link_path, self.catalog)
            self.assertFalse(audit["valid"])
            self.assertEqual([d["code"] for d in audit["diagnostics"]], ["LFC-IO-001"])

    def test_read_regular_bytes_enforces_size_bound(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            oversized = Path(tmp) / "oversized.lifecycle"
            oversized.write_bytes(b"A" * 128)
            with self.assertRaises(OSError):
                lifecycle.read_regular_bytes(oversized, max_bytes=64)

    def test_load_catalog_rejects_symlink_non_finite_and_deep_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            link_cat = tmp_dir / "catalog-link.json"
            link_cat.symlink_to(CATALOG_PATH)
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(link_cat)

            nan_cat = tmp_dir / "nan-catalog.json"
            nan_cat.write_text(
                '{"schema": "lifecycle.diagnostics/v1", "version": NaN, "diagnostics": []}',
                encoding="utf-8",
            )
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(nan_cat)

            nested = "[" * 32 + "]" * 32
            deep_cat = tmp_dir / "deep-catalog.json"
            deep_cat.write_text(
                f'{{"schema": "lifecycle.diagnostics/v1", "version": 1, "diagnostics": {nested}}}',
                encoding="utf-8",
            )
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(deep_cat)

            overflow_cat = tmp_dir / "overflow-catalog.json"
            overflow_cat.write_text(
                '{"schema": "lifecycle.diagnostics/v1", "version": 1e999, "diagnostics": []}',
                encoding="utf-8",
            )
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(overflow_cat)

    def test_huge_version_digits_and_fifo_fail_closed_without_crash_or_hang(self) -> None:
        huge_digits = "1" + ("0" * 5000)
        text = (
            f"LIFECYCLE sample VERSION {huge_digits}\n"
            "STATE START INITIAL\n"
            "STATE DONE TERMINAL\n"
            "EVENT GO\n"
            "TRANSITION START -> DONE ON GO\n"
            "END\n"
        )
        report = lifecycle.validate_text(text, source="huge.lifecycle", catalog=self.catalog)
        self.assertFalse(report.valid)
        self.assertIn("LFC-MODEL-001", {d.code for d in report.diagnostics})

        import os

        if hasattr(os, "mkfifo"):
            with tempfile.TemporaryDirectory() as tmp:
                fifo = Path(tmp) / "bundle.fifo"
                os.mkfifo(fifo)
                fifo_report = lifecycle.validate_path(fifo, self.catalog)
                self.assertFalse(fifo_report.valid)
                self.assertEqual([d.code for d in fifo_report.diagnostics], ["LFC-IO-001"])

    def test_nul_bytes_are_rejected_as_syntax_diagnostics(self) -> None:
        text = (
            "LIFECYCLE sample VERSION 1\n"
            "STATE START INITIAL\n"
            "STATE DONE\x00 TERMINAL\n"
            "EVENT GO\n"
            "TRANSITION START -> DONE ON GO\n"
            "END\n"
        )
        report = lifecycle.validate_text(text, source="nul.lifecycle", catalog=self.catalog)
        self.assertFalse(report.valid)
        self.assertIn("LFC-SYNTAX-002", {d.code for d in report.diagnostics})

    def test_duplicate_and_invalid_declarations_do_not_pollute_compaction_audit(self) -> None:
        text = """LIFECYCLE sample VERSION 1
STATE START INITIAL
STATE MID_A
STATE MID_B
STATE MID_A
STATE bad_name
STATE DONE TERMINAL
EVENT GO_A
EVENT GO_B
EVENT GO_A
EVENT 9_BAD
TRANSITION START -> MID_A ON GO_A
TRANSITION MID_A -> MID_B ON GO_B
TRANSITION MID_B -> DONE ON GO_A
END
"""
        audit = lifecycle.audit_compaction(text, source="dup.lifecycle", catalog=self.catalog)
        self.assertFalse(audit["valid"])
        codes = {f["code"] for f in audit["findings"]}
        self.assertNotIn("LFC-COMPACT-001", codes)
        self.assertNotIn("LFC-COMPACT-002", codes)

    def test_standalone_copied_validator_rejects_symlink_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            copied_module = tmp_dir / "lifecycle.py"
            copied_module.write_bytes((ROOT / "src" / "lifecycle.py").read_bytes())
            link_path = tmp_dir / "linked.lifecycle"
            link_path.symlink_to(PROFILE_PATH)
            result = subprocess.run(
                [sys.executable, str(copied_module), "validate", str(link_path), "--format", "json"],
                cwd=tmp,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual([d["code"] for d in payload["diagnostics"]], ["LFC-IO-001"])

    def test_lone_surrogates_and_control_bytes_fail_closed_in_bundle_and_catalog(self) -> None:
        surrogate_bundle = (
            "LIFECYCLE sample VERSION 1\n"
            "DESCRIPTION \"bad \ud800 text\"\n"
            "STATE START INITIAL\n"
            "STATE DONE TERMINAL\n"
            "EVENT GO\n"
            "TRANSITION START -> DONE ON GO\n"
            "END\n"
        )
        rep = lifecycle.validate_text(surrogate_bundle, source="surrogate.lifecycle", catalog=self.catalog)
        self.assertFalse(rep.valid)
        self.assertEqual([d.code for d in rep.diagnostics], ["LFC-SYNTAX-001"])

        ctrl_bundle = (
            "LIFECYCLE sample VERSION 1\n"
            "DESCRIPTION \"bad \x1b escape\"\n"
            "STATE START INITIAL\n"
            "STATE DONE TERMINAL\n"
            "EVENT GO\n"
            "TRANSITION START -> DONE ON GO\n"
            "END\n"
        )
        ctrl_rep = lifecycle.validate_text(ctrl_bundle, source="ctrl.lifecycle", catalog=self.catalog)
        self.assertFalse(ctrl_rep.valid)
        self.assertIn("LFC-SYNTAX-002", {d.code for d in ctrl_rep.diagnostics})

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            huge_int_cat = tmp_dir / "huge-int-catalog.json"
            huge_int_cat.write_text(
                '{"schema": "lifecycle.diagnostics/v1", "version": ' + ("9" * 400) + ', "diagnostics": []}',
                encoding="utf-8",
            )
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(huge_int_cat)

            surrogate_cat = tmp_dir / "surrogate-catalog.json"
            surrogate_cat.write_text(
                '{"schema": "lifecycle.diagnostics/v1", "version": 1, "diagnostics": [{"code": "\\ud800"}]}',
                encoding="utf-8",
            )
            with self.assertRaises(lifecycle.CatalogError):
                lifecycle.load_catalog(surrogate_cat)

    def test_read_regular_bytes_enforces_max_bytes_types_inode_swap_and_symlink_ancestors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            sample = base / "ok.lifecycle"
            sample.write_bytes(PROFILE_PATH.read_bytes())

            for bad_max in (True, False, 0, -1):
                with self.subTest(max_bytes=bad_max), self.assertRaises(ValueError):
                    lifecycle.read_regular_bytes(sample, max_bytes=bad_max)  # type: ignore[arg-type]

            real_fstat = os.fstat

            def fake_fstat(fd: int) -> os.stat_result:
                st = real_fstat(fd)
                return os.stat_result(
                    (
                        st.st_mode,
                        st.st_ino + 123456,
                        st.st_dev,
                        st.st_nlink,
                        st.st_uid,
                        st.st_gid,
                        st.st_size,
                        st.st_atime,
                        st.st_mtime,
                        st.st_ctime,
                    )
                )

            with mock.patch("os.fstat", side_effect=fake_fstat), self.assertRaises(OSError):
                lifecycle.read_regular_bytes(sample)

            outside = base / "outside"
            outside.mkdir()
            (outside / "secret.lifecycle").write_bytes(PROFILE_PATH.read_bytes())
            work = base / "work"
            work.mkdir()
            (work / "symdir").symlink_to(outside)
            old_cwd = Path.cwd()
            try:
                os.chdir(work)
                with self.assertRaises(OSError):
                    lifecycle.read_regular_bytes(Path("symdir/secret.lifecycle"))
            finally:
                os.chdir(old_cwd)

    def test_regex_anchors_reject_leading_newlines(self) -> None:
        self.assertIsNone(lifecycle.IDENTIFIER.fullmatch("\nSTART"))
        self.assertIsNone(lifecycle.LIFECYCLE_NAME.fullmatch("\nsample"))
        self.assertIsNone(lifecycle.CORE_CODE.fullmatch("\nLFC-IO-001"))


if __name__ == "__main__":
    unittest.main()
