"""Strict external catalog loader for Lifecycle DSL v1 diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lifecycle import CatalogEntry

MAX_CATALOG_DEPTH = 16


def _check_json_depth(value: Any, max_depth: int = MAX_CATALOG_DEPTH) -> None:
    from lifecycle import CatalogError

    stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop()
        if isinstance(current, dict):
            if depth >= max_depth:
                raise CatalogError(f"LFC-CATALOG-001: JSON nesting exceeds {max_depth}")
            for key, child in current.items():
                if not isinstance(key, str):
                    raise CatalogError("LFC-CATALOG-001: JSON object key must be a string")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            if depth >= max_depth:
                raise CatalogError(f"LFC-CATALOG-001: JSON nesting exceeds {max_depth}")
            for child in current:
                stack.append((child, depth + 1))


def load_catalog_impl(path: Path) -> dict[str, CatalogEntry]:
    from lifecycle import (
        CATALOG_SCHEMA,
        CORE_CODE,
        REQUIRED_CORE_CODES,
        SEVERITIES,
        CatalogEntry,
        CatalogError,
        read_regular_bytes,
    )

    def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, val in pairs:
            if not isinstance(key, str):
                raise CatalogError("LFC-CATALOG-001: JSON object key must be a string")
            if key in obj:
                raise CatalogError(f"LFC-CATALOG-001: duplicate JSON key {key!r}")
            obj[key] = val
        return obj

    def reject_constant(token: str) -> Any:
        raise CatalogError(f"LFC-CATALOG-001: non-finite JSON constant {token!r}")

    try:
        raw = read_regular_bytes(path).decode("utf-8")
        document = json.loads(
            raw, object_pairs_hook=strict_object, parse_constant=reject_constant
        )
    except CatalogError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise CatalogError(f"LFC-CATALOG-001: cannot load {path}: {error}") from error
    _check_json_depth(document)
    if not isinstance(document, dict) or set(document) != {
        "schema",
        "version",
        "diagnostics",
    }:
        raise CatalogError("LFC-CATALOG-001: catalog fields are invalid")
    version = document["version"]
    if document["schema"] != CATALOG_SCHEMA or type(version) is not int or version != 1:
        raise CatalogError("LFC-CATALOG-001: catalog schema or version is unsupported")
    rows = document["diagnostics"]
    if not isinstance(rows, list):
        raise CatalogError("LFC-CATALOG-001: diagnostics must be an array")
    result: dict[str, CatalogEntry] = {}
    for idx, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"code", "severity", "message"}:
            raise CatalogError(f"LFC-CATALOG-001: diagnostic {idx} fields are invalid")
        code, severity, msg = row["code"], row["severity"], row["message"]
        if (
            not isinstance(code, str)
            or CORE_CODE.fullmatch(code) is None
            or not isinstance(severity, str)
            or severity not in SEVERITIES
            or not isinstance(msg, str)
            or not msg.strip()
            or code in result
        ):
            raise CatalogError(f"LFC-CATALOG-001: diagnostic {idx} is invalid")
        result[code] = CatalogEntry(code, severity, msg)
    if set(result) != REQUIRED_CORE_CODES:
        missing = sorted(REQUIRED_CORE_CODES - set(result))
        extra = sorted(set(result) - REQUIRED_CORE_CODES)
        raise CatalogError(
            f"LFC-CATALOG-001: code set differs; missing={missing}, extra={extra}"
        )
    return result
