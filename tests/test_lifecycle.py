from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import lifecycle

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "errors" / "catalog.json"
PROFILE_PATH = ROOT / "profiles" / "reference.lifecycle"
ECOSYSTEM_PROFILE_PATH = ROOT / "profiles" / "wellmanifest-ecosystem.lifecycle"


def document(body: str) -> str:
    return f"""LIFECYCLE example VERSION 1
STATE START INITIAL
STATE DONE TERMINAL
EVENT COMPLETE
{body}
END
"""


class LifecycleValidationTests(unittest.TestCase):
    catalog: dict[str, lifecycle.CatalogEntry]

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = lifecycle.load_catalog(CATALOG_PATH)

    def validate(self, text: str) -> lifecycle.ValidationReport:
        return lifecycle.validate_text(
            text, source="fixture.lifecycle", catalog=self.catalog
        )

    def codes(self, text: str) -> set[str]:
        return {item.code for item in self.validate(text).diagnostics}

    def test_catalog_is_closed_and_complete(self) -> None:
        self.assertEqual(set(self.catalog), lifecycle.REQUIRED_CORE_CODES)
        self.assertEqual(self.catalog, lifecycle.embedded_catalog())

    def test_reference_bundle_validates_two_independent_domains(self) -> None:
        report = lifecycle.validate_path(PROFILE_PATH, self.catalog)
        self.assertTrue(report.valid, lifecycle.render_text(report))
        self.assertEqual(
            [item.name for item in report.lifecycles], ["git-branch", "governed-ticket"]
        )
        self.assertEqual(report.lifecycles[0].summary()["initial_state"], "ABSENT")
        self.assertEqual(
            report.lifecycles[1].summary()["terminal_states"], ["CANCELLED", "DONE"]
        )
        self.assertTrue(
            any(
                transition.source == "ACTIVE"
                and transition.target == "ARCHIVED"
                and transition.event == "ARCHIVE"
                and transition.evidence == "OWNER_DISCARD_DECISION"
                for transition in report.lifecycles[0].transitions
            )
        )

    def test_ecosystem_bundle_validates_all_lifecycle_domains(self) -> None:
        report = lifecycle.validate_path(ECOSYSTEM_PROFILE_PATH, self.catalog)
        self.assertTrue(report.valid, lifecycle.render_text(report))
        self.assertEqual(
            [item.name for item in report.lifecycles],
            [
                "git-repository",
                "governed-ticket",
                "legal-obligation",
                "product-release",
                "saas-tenant",
                "twin-stage",
            ],
        )
        by_name = {item.name: item for item in report.lifecycles}
        expected_boundaries = {
            "git-repository": ("UNINITIALIZED", ["TERMINAL"]),
            "governed-ticket": ("UNALLOCATED", ["DONE"]),
            "legal-obligation": ("UNBOUND", ["DENIED", "EXPIRED"]),
            "product-release": ("DRAFT", ["SUNSET"]),
            "saas-tenant": ("REQUESTED", ["CANCELLED", "EXPIRED", "FAILED"]),
            "twin-stage": ("CONCEPT", ["RETIRED"]),
        }
        for name, (initial, terminals) in expected_boundaries.items():
            with self.subTest(lifecycle=name):
                summary = by_name[name].summary()
                self.assertEqual(summary["initial_state"], initial)
                self.assertEqual(summary["terminal_states"], terminals)
        self.assertTrue(
            any(
                item.source == "ACTIVE"
                and item.target == "ACTIVE"
                and item.event == "PURCHASE_ADDON"
                for item in by_name["saas-tenant"].transitions
            )
        )
        self.assertTrue(
            any(
                item.source == "EVOLVING"
                and item.target == "OPERATING"
                and item.event == "STABILIZE"
                for item in by_name["twin-stage"].transitions
            )
        )

    def test_validator_copy_runs_without_repository_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied_module = Path(temporary) / "lifecycle.py"
            copied_module.write_bytes((ROOT / "src" / "lifecycle.py").read_bytes())
            result = subprocess.run(
                [
                    sys.executable,
                    str(copied_module),
                    "validate",
                    str(ECOSYSTEM_PROFILE_PATH),
                    "--format",
                    "json",
                ],
                cwd=temporary,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["lifecycle_count"], 6)

    def test_report_serialization_is_deterministic(self) -> None:
        first = lifecycle.validate_path(PROFILE_PATH, self.catalog).as_dict()
        second = lifecycle.validate_path(PROFILE_PATH, self.catalog).as_dict()
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_unknown_statement_is_rejected(self) -> None:
        self.assertIn("LFC-SYNTAX-002", self.codes(document("EXECUTE COMPLETE")))

    def test_empty_bundle_is_rejected(self) -> None:
        self.assertIn("LFC-DOC-001", self.codes("# comments only\n"))

    def test_unsupported_document_version_is_rejected(self) -> None:
        text = document("TRANSITION START -> DONE ON COMPLETE").replace(
            "VERSION 1", "VERSION 2"
        )
        self.assertIn("LFC-MODEL-001", self.codes(text))

    def test_duplicate_state_is_rejected(self) -> None:
        text = document("STATE START\nTRANSITION START -> DONE ON COMPLETE")
        self.assertIn("LFC-MODEL-002", self.codes(text))

    def test_missing_initial_state_is_rejected(self) -> None:
        text = """LIFECYCLE example VERSION 1
STATE START
END
"""
        self.assertIn("LFC-MODEL-003", self.codes(text))

    def test_undeclared_reference_is_rejected(self) -> None:
        text = document("TRANSITION START -> MISSING ON COMPLETE")
        self.assertIn("LFC-MODEL-004", self.codes(text))

    def test_nondeterministic_state_event_pair_is_rejected(self) -> None:
        text = document(
            "TRANSITION START -> DONE ON COMPLETE\n"
            "TRANSITION START -> START ON COMPLETE"
        )
        self.assertIn("LFC-MODEL-005", self.codes(text))

    def test_unreachable_state_is_rejected(self) -> None:
        text = document("STATE ORPHAN\nTRANSITION START -> DONE ON COMPLETE")
        self.assertIn("LFC-MODEL-006", self.codes(text))

    def test_terminal_outgoing_transition_is_rejected(self) -> None:
        text = document(
            "TRANSITION START -> DONE ON COMPLETE\nTRANSITION DONE -> DONE ON COMPLETE"
        )
        self.assertIn("LFC-MODEL-007", self.codes(text))

    def test_reject_must_bind_declared_error(self) -> None:
        text = document("REJECT START ON COMPLETE WITH EXAMPLE-ERROR-001")
        self.assertIn("LFC-ERROR-002", self.codes(text))

    def test_declared_error_must_be_used(self) -> None:
        text = document(
            "TRANSITION START -> DONE ON COMPLETE\n"
            'ERROR EXAMPLE-ERROR-001 SEVERITY ERROR MESSAGE "unused"'
        )
        self.assertIn("LFC-ERROR-002", self.codes(text))

    def test_invalid_profile_error_code_is_rejected(self) -> None:
        text = document('ERROR BAD SEVERITY ERROR MESSAGE "bad code"')
        self.assertIn("LFC-ERROR-001", self.codes(text))

    def test_profile_error_cannot_use_reserved_core_prefix(self) -> None:
        text = document('ERROR LFC-USER-001 SEVERITY ERROR MESSAGE "reserved"')
        self.assertIn("LFC-ERROR-001", self.codes(text))

    def test_document_text_never_executes_shell_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "executed"
            text = document(
                "TRANSITION START -> DONE ON COMPLETE\n"
                f'ERROR EXAMPLE-ERROR-001 SEVERITY ERROR MESSAGE "$(touch {marker})"\n'
                "REJECT DONE ON COMPLETE WITH EXAMPLE-ERROR-001"
            )
            self.validate(text)
            self.assertFalse(marker.exists())

    def test_cli_text_and_json_contracts(self) -> None:
        environment = {"PYTHONPATH": str(ROOT / "src")}
        text = subprocess.run(
            [sys.executable, "-m", "lifecycle", "validate", str(PROFILE_PATH)],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn("PASS", text.stdout)
        structured = subprocess.run(
            [
                sys.executable,
                "-m",
                "lifecycle",
                "validate",
                str(PROFILE_PATH),
                "--format",
                "json",
            ],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(structured.returncode, 0, structured.stderr)
        self.assertEqual(json.loads(structured.stdout)["status"], "valid")

    def test_cli_invalid_input_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.lifecycle"
            path.write_text(document("UNKNOWN"), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                result = lifecycle.main(
                    ["validate", str(path), "--catalog", str(CATALOG_PATH)]
                )
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
