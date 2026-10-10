#!/usr/bin/env python3
"""Read-only validation of a Nasaq selection manifest, not an agent sandbox.

No provider code is imported, installed, downloaded or executed. A zero exit
status means declared constraints passed, not that integrations were exercised.
Python 3.11+; standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2 * 1024 * 1024
ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ROLES = {"primary", "reviewer", "reference", "executor"}
PHASES = {"discovery", "planning", "design", "implementation", "verification", "release"}
MODES = {"builtin", "workflow-reference", "reviewed-cli", "native-tool", "versioned-reference"}
INSTRUCTION_KINDS = {"skill", "instruction-library", "workflow"}
PROVIDER_KINDS = INSTRUCTION_KINDS | {"builtin", "tool", "review-instructions", "official-reference", "standard"}
BIDI = set("\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    if path.is_symlink() or not path.is_file():
        raise ValueError("input must be a regular, non-symlink JSON file")
    with path.open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("JSON input exceeds size limit")
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=_unique_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("non-finite number")))


def plan_digest(plan: dict[str, Any]) -> str:
    body = {key: value for key, value in plan.items() if key != "approval"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=True,
                                     allow_nan=False, separators=(",", ":")).encode()).hexdigest()


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and ID.fullmatch(value) is not None


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) and x for x in value)


def _write_path(value: Any) -> str | None:
    if not _nonempty(value) or value.startswith("/") or "\\" in value or ":" in value:
        return None
    if any(ord(c) < 32 or c in BIDI for c in value) or any(c in value for c in "*?[]"):
        return None
    parts = value.rstrip("/").split("/")
    if not parts or any(p in {"", ".", ".."} or p.endswith((" ", ".")) for p in parts):
        return None
    reserved = {"con", "prn", "aux", "nul"} | {f"{s}{n}" for s in ["com", "lpt"] for n in range(1,10)}
    if any(p.split(".")[0].casefold() in reserved for p in parts):
        return None
    return "/".join(parts).casefold()


def validate_selection(plan: Any, registry: Any, capabilities: Any, *, ready: bool = False) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    def error(code: str, location: str) -> None:
        issues.append({"code": code, "location": location, "severity": "error"})

    if not isinstance(plan, dict) or type(plan.get("schema_version")) is not int or plan["schema_version"] != 1:
        error("invalid_plan", "$")
        return issues
    if not isinstance(registry, dict) or not isinstance(registry.get("providers"), list):
        error("invalid_registry", "registry")
        return issues
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("capabilities"), list):
        error("invalid_registry", "capabilities")
        return issues
    providers: dict[str, dict[str, Any]] = {}
    for i, source in enumerate(registry["providers"]):
        if (not isinstance(source, dict) or not _valid_id(source.get("id"))
                or source["id"] in providers or not isinstance(source.get("kind"),str)
                or source["kind"] not in PROVIDER_KINDS
                or not _valid_id(source.get("lineage_group",source["id"]))
                or not _strings(source.get("capabilities"))
                or not isinstance(source.get("eligibility"), dict)
                or not _strings(source["eligibility"].get("any_of_tags"))):
            error("invalid_registry", f"providers[{i}]")
            continue
        providers[source["id"]] = source
    caps: set[str] = set()
    for i, cap in enumerate(capabilities["capabilities"]):
        if not isinstance(cap, dict) or not _valid_id(cap.get("id")) or cap["id"] in caps:
            error("invalid_registry", f"capabilities[{i}]")
        else:
            caps.add(cap["id"])
    for pid, source in providers.items():
        if not set(source["capabilities"]).issubset(caps):
            error("invalid_registry", f"providers[{pid}].capabilities")
    if issues:
        return issues
    components = plan.get("components")
    if not isinstance(components, dict) or not components:
        error("invalid_components", "components")
        return issues
    for name, obj in components.items():
        if not _valid_id(name) or not isinstance(obj, dict) or not _strings(obj.get("tags")) or not obj["tags"]:
            error("invalid_components", "components")
    bindings = plan.get("bindings")
    required = plan.get("required_slots")
    conflicts = plan.get("activation_conflicts")
    if not isinstance(bindings, list) or not isinstance(required, list) or not isinstance(conflicts, list):
        error("invalid_plan", "bindings/required_slots/activation_conflicts")
        return issues
    if issues:
        return issues
    ids: set[str] = set()
    primaries: dict[tuple[str,str,str], str] = {}
    occupied: set[tuple[str,str,str,str]] = set()
    writers: list[tuple[str,str,str]] = []
    lineages: dict[tuple[str,str,str], str] = {}
    for i, binding in enumerate(bindings):
        loc = f"bindings[{i}]"
        if not isinstance(binding, dict):
            error("invalid_binding", loc)
            continue
        bid = binding.get("id")
        if not _valid_id(bid) or bid in ids:
            error("duplicate_or_invalid_id", loc)
            continue
        ids.add(bid)
        source = providers.get(binding.get("provider")) if isinstance(binding.get("provider"), str) else None
        if source is None:
            error("unknown_provider", loc)
            continue
        cap, comp, phase, role = (binding.get(k) for k in ["capability", "component", "phase", "role"])
        if (not isinstance(cap,str) or cap not in caps or cap not in source["capabilities"]
                or not isinstance(comp,str) or comp not in components
                or not isinstance(phase,str) or phase not in PHASES
                or not isinstance(role,str) or role not in ROLES):
            error("invalid_scope", loc)
            continue
        if not _nonempty(binding.get("scope_contract")):
            error("missing_contract", loc)
        tag_options = set(source["eligibility"]["any_of_tags"])
        if "any" not in tag_options and not tag_options.intersection(components[comp]["tags"]):
            error("stack_mismatch", loc)
        if source["kind"] == "tool" and role != "executor":
            error("tool_role", loc)
        if source["kind"] == "review-instructions" and role != "reviewer":
            error("reviewer_role", loc)
        if source["kind"] in {"official-reference", "standard"} and role != "reference":
            error("reference_role", loc)
        if source["kind"] in INSTRUCTION_KINDS and role in {"reference", "reviewer"} and not _nonempty(binding.get("adaptation_note")):
            error("adaptation_required", loc)
        slot = (cap, comp, phase)
        occupied.add((cap,comp,phase,role))
        if role == "primary":
            if slot in primaries:
                error("duplicate_primary", loc)
            primaries[slot] = bid
            lineage = (source.get("lineage_group", source["id"]), comp, phase)
            if lineage in lineages and lineages[lineage] != source["id"]:
                error("duplicate_lineage", loc)
            lineages[lineage] = source["id"]
        writes = binding.get("writes")
        if not _strings(writes):
            error("invalid_writes", loc)
            writes=[]
        if role in {"reviewer", "reference"} and writes:
            error("read_only_role_writes", loc)
        for write in writes:
            norm=_write_path(write)
            if norm is None:
                error("unsafe_write_path", loc)
                continue
            for old, oldphase, oldid in writers:
                if oldphase == phase and oldid != bid and (norm==old or norm.startswith(old+"/") or old.startswith(norm+"/")):
                    error("output_overlap", loc)
            writers.append((norm,phase,bid))
        mode = binding.get("activation_mode")
        if not isinstance(mode,str) or mode not in MODES:
            error("invalid_mode", loc)
        if isinstance(mode,str) and mode in {"native-tool", "reviewed-cli"} and source["kind"] in {"official-reference", "standard"}:
            error("reference_not_executable", loc)
        if ready and source["kind"] != "builtin":
            resolved=binding.get("resolved")
            if not isinstance(resolved,dict):
                error("unresolved_source", loc)
                continue
            pin=resolved.get("pinned_ref")
            if (not _nonempty(pin) or pin.casefold() in {"main","master","head","latest"}
                    or "@latest" in pin.casefold()):
                error("unpinned_source", loc)
            if not isinstance(resolved.get("sha256"),str) or not HEX64.fullmatch(resolved["sha256"]):
                error("missing_digest", loc)
            for field,code in [("license_reviewed","license_pending"),("scope_reviewed","scope_pending"),("permissions_approved","permissions_pending")]:
                if resolved.get(field) is not True:
                    error(code,loc)
            if isinstance(mode,str) and mode in {"native-tool", "reviewed-cli"} and resolved.get("adapter_status") != "tested":
                error("adapter_unverified",loc)
    req_ids:set[tuple[str,str,str,str]]=set()
    for i, req in enumerate(required):
        loc=f"required_slots[{i}]"
        if not isinstance(req,dict):
            error("invalid_required_slot",loc)
            continue
        vals=tuple(req.get(k) for k in ["capability","component","phase","role"])
        if not all(isinstance(v,str) for v in vals) or vals[0] not in caps or vals[1] not in components or vals[2] not in PHASES or vals[3] not in ROLES:
            error("invalid_required_slot",loc)
            continue
        if vals in req_ids:
            error("invalid_required_slot",loc)
        req_ids.add(vals)
        if vals not in occupied:
            error("uncovered_slot",loc)
    for i, conflict in enumerate(conflicts):
        loc=f"activation_conflicts[{i}]"
        if (not isinstance(conflict,dict) or conflict.get("status") not in {"unresolved","isolated","removed_with_approval"}
                or not _nonempty(conflict.get("source"))):
            error("invalid_conflict",loc)
        elif conflict["status"]=="unresolved":
            error("active_conflict",loc)
        elif not _nonempty(conflict.get("evidence_ref")):
            error("conflict_without_evidence",loc)
    if ready:
        approval=plan.get("approval")
        if not isinstance(approval,dict) or approval.get("confirmed_by_user") is not True or approval.get("plan_sha256")!=plan_digest(plan):
            error("stale_or_missing_approval","approval")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan",type=Path)
    parser.add_argument("--ready",action="store_true",help="Check declared resolution and approval fields; never run providers")
    parser.add_argument("--lang",choices=["ar","en"],default="ar")
    parser.add_argument("--json",action="store_true")
    parser.add_argument("--registry",type=Path,default=ROOT/"assets/providers.json")
    parser.add_argument("--capabilities",type=Path,default=ROOT/"assets/capabilities.json")
    args=parser.parse_args(argv)
    locale=load_json(ROOT/"assets/validator_messages.json")[args.lang]
    try:
        plan=load_json(args.plan)
        issues=validate_selection(plan,load_json(args.registry),load_json(args.capabilities),ready=args.ready)
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        # Do not echo raw input or secrets in error messages.
        if args.json:
            print(json.dumps({"status":"input_error","message":locale["input_error"],"error_type":type(exc).__name__},ensure_ascii=False))
        else:
            print(locale["input_error"],file=sys.stderr)
        return 2
    result={"status":"invalid" if issues else "declared_constraints_passed","ready_fields_checked":args.ready,
            "issues":[dict(x,message=locale.get(x["code"],x["code"])) for x in issues],
            "limitation":locale["limitation"]}
    if args.json:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(locale["invalid"] if issues else locale["ok"])
        for x in result["issues"]:
            print(f'{x["code"]}: {x["location"]}: {x["message"]}')
        print(locale["limitation"])
    return 1 if issues else 0

if __name__=="__main__":
    raise SystemExit(main())
