#!/usr/bin/env python3
"""Validate prepared web research mappings, never activate or execute providers."""
from __future__ import annotations

import argparse
import json
from typing import Any

from check_selection import ROOT, PROVIDER_KINDS, load_json, _valid_id, _strings

RELATIONS = {"single", "alternatives", "complements", "scoped-complements"}


def validate_web_catalog(source_map: Any, coverage: Any, registry: Any, capabilities: Any) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    def error(code: str, location: str) -> None:
        issues.append({"code": code, "location": location, "severity": "error"})

    for name, obj, key in [("map", source_map, "sources"), ("coverage", coverage, "rows"),
                           ("registry", registry, "providers"), ("capabilities", capabilities, "capabilities")]:
        if (not isinstance(obj, dict) or type(obj.get("schema_version")) is not int
                or obj["schema_version"] != 1 or not isinstance(obj.get(key), list)):
            error("web_invalid_structure", name)
    if issues:
        return issues
    if source_map.get("automatic_activation_allowed") is not False:
        error("web_activation_forbidden", "map.automatic_activation_allowed")
    if source_map.get("scope") != ["web"] or coverage.get("scope") != ["web"]:
        error("web_invalid_scope", "scope")

    def index(items: list, location: str) -> dict:
        result: dict = {}
        for i, item in enumerate(items):
            if not isinstance(item, dict) or not _valid_id(item.get("id")) or item["id"] in result:
                error("web_invalid_id", f"{location}[{i}]")
            else:
                result[item["id"]] = item
        return result

    providers = index(registry["providers"], "providers")
    caps = index(capabilities["capabilities"], "capabilities")
    sources = index(source_map["sources"], "sources")
    rows = index(coverage["rows"], "rows")
    if issues:
        return issues
    for pid, provider in providers.items():
        kind = provider.get("kind")
        if (not isinstance(kind, str) or kind not in PROVIDER_KINDS
                or not _strings(provider.get("capabilities"))
                or not set(provider["capabilities"]).issubset(caps)):
            error("web_invalid_provider", pid)
    original_ids = source_map.get("original_provider_ids")
    if not _strings(original_ids) or not set(original_ids).issubset(providers):
        error("web_unknown_provider", "map.original_provider_ids")
    if issues:
        return issues
    for sid, source in sources.items():
        if sid != "web." + str(source.get("research_id", "")).lower():
            error("web_invalid_id", sid)
        if (source.get("status") != "research_candidate" or source.get("installed") is not False
                or source.get("runtime_tested") is not False):
            error("web_activation_forbidden", sid)
        targets = source.get("targets")
        relation = source.get("relation")
        if (not isinstance(targets, list) or not targets or not isinstance(relation, str)
                or relation not in RELATIONS or (relation == "single" and len(targets) != 1)):
            error("web_invalid_relation", sid)
            continue
        seen = set()
        for i, target in enumerate(targets):
            loc = f"{sid}.targets[{i}]"
            if not isinstance(target, dict) or not _valid_id(target.get("provider_id")):
                error("web_unknown_provider", loc)
                continue
            pid = target["provider_id"]
            if pid not in providers or pid in seen:
                error("web_unknown_provider", loc)
                continue
            seen.add(pid)
            kind = providers[pid]["kind"]
            expected = ("executor" if kind == "tool" else "reviewer" if kind == "review-instructions"
                        else "reference" if kind in {"official-reference", "standard"} else "primary")
            if target.get("role") != expected:
                error("web_invalid_role", loc)
    for wid, row in rows.items():
        if wid != "web." + str(row.get("research_id", "")).lower():
            error("web_invalid_id", wid)
        if row.get("implementation_status") != "research_mapping_only":
            error("web_activation_forbidden", wid)
        if (not isinstance(row.get("applicability"), str)
                or row["applicability"] not in {"required", "optional", "not_applicable", "unknown"}):
            error("web_invalid_scope", wid)
        if not _strings(row.get("capability_ids")) or not row["capability_ids"] or not set(row["capability_ids"]).issubset(caps):
            error("web_unknown_capability", wid)
        proposed = row.get("proposed_source_refs")
        supporting = row.get("supporting_source_refs")
        if not _strings(proposed) or not proposed or not _strings(supporting):
            error("web_unknown_source", wid)
            continue
        if not set(proposed + supporting).issubset(sources):
            error("web_unknown_source", wid)
        relation = row.get("source_relation")
        if (not isinstance(relation, str) or relation not in RELATIONS
                or (relation == "single" and len(proposed) != 1)):
            error("web_invalid_relation", wid)
    for field, ref_field, allowed in [("gaps", "topics", rows), ("conflict_rules", "sources", sources),
                                      ("evaluations", "sources", sources)]:
        entries = coverage.get(field)
        if not isinstance(entries, list):
            error("web_invalid_structure", field)
            continue
        entries_by_id = index(entries, field)
        for eid, entry in entries_by_id.items():
            if eid != "web." + str(entry.get("research_id", "")).lower():
                error("web_invalid_id", eid)
            refs = entry.get(ref_field)
            if not _strings(refs) or not set(refs).issubset(allowed):
                error("web_unknown_source", eid)
            if field == "evaluations" and (entry.get("status") != "not_run" or entry.get("result") is not None
                                           or entry.get("evidence_paths") != []):
                error("web_activation_forbidden", eid)
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    from pathlib import Path
    parser.add_argument("--map", type=Path, default=ROOT / "assets/web-source-map.json")
    parser.add_argument("--coverage", type=Path, default=ROOT / "assets/web-coverage.json")
    parser.add_argument("--registry", type=Path, default=ROOT / "assets/providers.json")
    parser.add_argument("--capabilities", type=Path, default=ROOT / "assets/capabilities.json")
    parser.add_argument("--lang", choices=["ar", "en"], default="ar")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    locale = load_json(ROOT / "assets/validator_messages.json")[args.lang]
    try:
        issues = validate_web_catalog(load_json(args.map), load_json(args.coverage),
                                      load_json(args.registry), load_json(args.capabilities))
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        result = {"status": "input_error", "message": locale["input_error"], "error_type": type(exc).__name__}
        print(json.dumps(result, ensure_ascii=False) if args.json else result["message"])
        return 2
    result = {"status": "invalid" if issues else "research_mapping_valid",
              "integrations_executed": False,
              "issues": [dict(issue, message=locale[issue["code"]]) for issue in issues],
              "limitation": locale["limitation"]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(locale["invalid"] if issues else locale["web_ok"])
        for issue in result["issues"]:
            print(f'{issue["code"]}: {issue["location"]}: {issue["message"]}')
        print(result["limitation"])
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
