"""
Workflow import — bring existing automation into Apex.

Teams already own their automation: Robot Framework certification suites and
Ansible provisioning playbooks. Apex should ingest those rather than ask anyone
to re-author them, so import is a first-class path, not a migration project.

Supported sources
-----------------
* **Robot Framework** `output.xml` — the artifact every certification run already
  produces. Tests become playbook steps; suite metadata becomes context; the
  keyword libraries used become the action mapping.
* **Ansible** playbook YAML — plays and tasks become steps; the modules used
  map onto Apex actions.

The importer *proposes* a playbook and shows how every source element mapped.
Nothing is written until the proposal is committed, so an engineer can see
exactly what Apex made of their file before it lands.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import structlog
import yaml

log = structlog.get_logger()

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOKS_DIR = ROOT / "playbooks"
SAMPLES_DIR = ROOT / "verizon-test-data"


# ─────────────────────────────────────────────────────────────────────────────
# format detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_format(content: str, filename: str = "") -> str:
    """Identify the source. Content wins over extension — filenames lie."""
    head = content.lstrip()[:600]
    name = filename.lower()

    if head.startswith("<?xml") or "<robot" in head:
        return "robot_framework" if "<robot" in content[:4000] else "xml"
    if name.endswith((".yml", ".yaml")) or head.startswith(("---", "- name:", "- hosts:")):
        try:
            doc = yaml.safe_load(content)
        except yaml.YAMLError:
            return "unknown"
        if isinstance(doc, list) and doc and isinstance(doc[0], dict):
            if any(k in doc[0] for k in ("hosts", "tasks", "roles")):
                return "ansible"
        if isinstance(doc, dict) and ("actions" in doc or "recipe" in doc):
            return "apex_playbook"
        return "yaml"
    return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Robot Framework
# ─────────────────────────────────────────────────────────────────────────────

# Keyword libraries observed in the certification suites, mapped onto the Apex
# actions that do the equivalent work. Anything unmapped is reported, not hidden.
ROBOT_LIBRARY_ACTIONS = {
    "VerizonEdgeLib":  "telecommunications.run_test_iterations",
    "RedfishLibrary":  "telecommunications.detect_schema_drift",
    "BuiltIn":         "telecommunications.parse_robot_output",
    "OperatingSystem": "telecommunications.parse_robot_output",
    "SSHLibrary":      "telecommunications.validate_upgrade_path",
    "RequestsLibrary": "telecommunications.detect_schema_drift",
}

# Test-name keywords → the classification stage that should own them.
ROBOT_TOPIC_ACTIONS = [
    (("latency", "throughput", "jitter", "packet"), "telecommunications.run_test_iterations"),
    (("redfish", "schema", "endpoint"),             "telecommunications.detect_schema_drift"),
    (("firmware", "upgrade", "version"),            "telecommunications.validate_upgrade_path"),
    (("cert", "secure", "boot", "key"),             "telecommunications.compute_risk_scores"),
]


def parse_robot(content: str) -> Dict[str, Any]:
    """Extract suite metadata, tests and outcomes from a Robot output.xml."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f"Not valid XML: {e}")

    if root.tag != "robot":
        raise ValueError("Not a Robot Framework output file (root element is not <robot>)")

    suite = root.find("suite")
    metadata: Dict[str, str] = {}
    if suite is not None:
        for item in suite.findall("./metadata/item"):
            key = item.get("name")
            if key:
                metadata[key] = (item.text or "").strip()

    tests: List[Dict[str, Any]] = []
    libraries: Counter = Counter()

    for test in root.iter("test"):
        status_el = test.find("status")
        # A test's own <status> is the last one at its level; keywords have their own.
        own_status = None
        for child in test:
            if child.tag == "status":
                own_status = child
        status = (own_status if own_status is not None else status_el)

        kws = []
        for kw in test.findall("kw"):
            lib = kw.get("library") or ""
            if lib:
                libraries[lib] += 1
            kws.append({
                "name": kw.get("name"),
                "library": lib,
                "args": [a.text for a in kw.findall("arg") if a.text],
            })

        messages = [
            {"level": m.get("level"), "text": (m.text or "").strip()}
            for m in test.iter("msg")
            if m.get("level") in ("FAIL", "WARN", "ERROR")
        ]

        tests.append({
            "id": test.get("id"),
            "name": test.get("name"),
            "status": (status.get("status") if status is not None else "UNKNOWN"),
            "keywords": kws,
            "failures": messages,
        })

    outcomes = Counter(t["status"] for t in tests)

    return {
        "generator": root.get("generator"),
        "generated": root.get("generated"),
        "suite_name": suite.get("name") if suite is not None else None,
        "suite_source": suite.get("source") if suite is not None else None,
        "metadata": metadata,
        "tests": tests,
        "test_count": len(tests),
        "outcomes": dict(outcomes),
        "libraries": dict(libraries),
    }


def action_for_test(test: Dict[str, Any]) -> Tuple[str, str]:
    """
    Choose the Apex action for a Robot test, and say why.

    Library binding is the stronger signal; the test name is the fallback so a
    suite using only BuiltIn still maps to something meaningful.
    """
    for kw in test.get("keywords", []):
        lib = kw.get("library")
        if lib and lib in ROBOT_LIBRARY_ACTIONS and lib != "BuiltIn":
            return ROBOT_LIBRARY_ACTIONS[lib], f"keyword library {lib}"

    name = (test.get("name") or "").lower()
    for needles, action in ROBOT_TOPIC_ACTIONS:
        if any(n in name for n in needles):
            hit = next(n for n in needles if n in name)
            return action, f"test name contains “{hit}”"

    for kw in test.get("keywords", []):
        lib = kw.get("library")
        if lib in ROBOT_LIBRARY_ACTIONS:
            return ROBOT_LIBRARY_ACTIONS[lib], f"keyword library {lib}"

    return "telecommunications.parse_robot_output", "default — no library or topic match"


def robot_to_playbook(parsed: Dict[str, Any], name_hint: str = "") -> Dict[str, Any]:
    """Compose an Apex playbook from a parsed Robot suite."""
    meta = parsed["metadata"]
    suite_name = parsed.get("suite_name") or name_hint or "Imported certification suite"
    slug = _slug(name_hint or suite_name)

    # Group tests by the action they map to; a 248-test suite becomes a handful
    # of playbook steps, not 248 of them.
    grouped: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    mapping: List[Dict[str, Any]] = []

    for test in parsed["tests"]:
        action_id, reason = action_for_test(test)
        entry = grouped.setdefault(action_id, {"count": 0, "examples": [], "failures": 0})
        entry["count"] += 1
        if len(entry["examples"]) < 3:
            entry["examples"].append(test["name"])
        if test["status"] == "FAIL":
            entry["failures"] += 1

        mapping.append({
            "source": test["name"],
            "source_type": "robot test",
            "status": test["status"],
            "action_id": action_id,
            "reason": reason,
        })

    actions = []
    for action_id, info in grouped.items():
        actions.append({
            "name": action_id.split(".")[-1],
            "action_id": action_id,
            "description": (
                f"Covers {info['count']} test"
                f"{'' if info['count'] == 1 else 's'} from the imported suite"
                + (f" ({info['failures']} currently failing)" if info["failures"] else "")
            ),
            "required": True,
        })

    outcomes = parsed["outcomes"]
    business_rules = [
        f"Source suite: {suite_name}",
        f"{parsed['test_count']} tests imported "
        f"({', '.join(f'{v} {k}' for k, v in outcomes.items())})",
    ]
    for k, v in meta.items():
        business_rules.append(f"{k.replace('_', ' ').title()}: {v}")

    playbook = {
        "name": slug,
        "version": "1.0.0",
        "description": f"Imported from Robot Framework suite “{suite_name}”",
        "industry": "telecommunications",
        "category": "certification",
        "intent": (
            f"Run the certification coverage previously held in the Robot Framework suite "
            f"“{suite_name}”. The suite contributed {parsed['test_count']} tests across "
            f"{len(grouped)} Apex actions. Failures are classified and raised as tickets "
            f"rather than left in a report no one reads."
        ),
        "output": [{
            "name": "certification_result",
            "type": "structured_data",
            "description": "Per-test outcome, classified failures, and raised tickets",
        }],
        "context": {"business_rules": business_rules},
        "actions": actions,
        "recipe": _robot_recipe(grouped, suite_name),
        "triggers": [{"type": "schedule", "cadence": "nightly"}],
    }

    return {"playbook": playbook, "mapping": mapping}


def _robot_recipe(grouped: Dict[str, Dict[str, Any]], suite_name: str) -> str:
    lines = [f"Imported from the Robot Framework suite “{suite_name}”.", ""]
    for i, (action_id, info) in enumerate(grouped.items(), start=1):
        examples = ", ".join(info["examples"][:2])
        lines.append(f"{i}. {action_id} — {info['count']} tests (e.g. {examples})")
    lines += [
        "",
        f"{len(grouped) + 1}. Classify any failure against the known-issues knowledge base.",
        f"{len(grouped) + 2}. Raise a ticket per unmatched failure, after human approval.",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Ansible
# ─────────────────────────────────────────────────────────────────────────────

# Ansible modules → the Apex action that performs the equivalent operation.
ANSIBLE_MODULE_ACTIONS = {
    "uri":              "telecommunications.detect_schema_drift",
    "redfish_command":  "telecommunications.detect_schema_drift",
    "redfish_config":   "telecommunications.apply_playbook_change",
    "redfish_info":     "telecommunications.detect_schema_drift",
    "community.general.redfish_command": "telecommunications.detect_schema_drift",
    "community.general.redfish_config":  "telecommunications.apply_playbook_change",
    "community.general.redfish_info":    "telecommunications.detect_schema_drift",
    "shell":            "telecommunications.run_test_iterations",
    "command":          "telecommunications.run_test_iterations",
    "script":           "telecommunications.run_test_iterations",
    "template":         "telecommunications.draft_playbook_change",
    "copy":             "telecommunications.apply_playbook_change",
    "assert":           "telecommunications.compute_risk_scores",
    "fail":             "telecommunications.classify_failures",
    "debug":            "telecommunications.parse_robot_output",
}

# Keys on a task that are directives, not the module being invoked.
ANSIBLE_TASK_DIRECTIVES = {
    "name", "when", "tags", "register", "vars", "become", "become_user", "loop",
    "with_items", "notify", "ignore_errors", "changed_when", "failed_when",
    "delegate_to", "run_once", "no_log", "retries", "delay", "until", "block",
    "rescue", "always", "environment", "args",
}


def parse_ansible(content: str) -> Dict[str, Any]:
    """Extract plays, tasks and modules from an Ansible playbook."""
    try:
        doc = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"Not valid YAML: {e}")

    if not isinstance(doc, list):
        raise ValueError("An Ansible playbook must be a list of plays")

    plays: List[Dict[str, Any]] = []
    modules: Counter = Counter()

    for play in doc:
        if not isinstance(play, dict):
            continue
        tasks: List[Dict[str, Any]] = []
        for section in ("pre_tasks", "tasks", "post_tasks"):
            for task in play.get(section) or []:
                if not isinstance(task, dict):
                    continue
                module = next(
                    (k for k in task
                     if k not in ANSIBLE_TASK_DIRECTIVES and not k.startswith("_")),
                    None,
                )
                if module:
                    modules[module] += 1
                tasks.append({
                    "name": task.get("name") or module or "unnamed task",
                    "module": module,
                    "section": section,
                    "when": task.get("when"),
                })

        plays.append({
            "name": play.get("name") or "unnamed play",
            "hosts": play.get("hosts"),
            "roles": [
                r if isinstance(r, str) else (r.get("role") or r.get("name"))
                for r in (play.get("roles") or [])
            ],
            "tasks": tasks,
        })

    return {
        "plays": plays,
        "play_count": len(plays),
        "task_count": sum(len(p["tasks"]) for p in plays),
        "modules": dict(modules),
        "roles": sorted({r for p in plays for r in p["roles"] if r}),
    }


def ansible_to_playbook(parsed: Dict[str, Any], name_hint: str = "") -> Dict[str, Any]:
    """Compose an Apex playbook from a parsed Ansible playbook."""
    title = name_hint or (parsed["plays"][0]["name"] if parsed["plays"] else "Imported playbook")
    slug = _slug(title)

    grouped: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    mapping: List[Dict[str, Any]] = []

    for play in parsed["plays"]:
        for task in play["tasks"]:
            module = task.get("module")
            action_id = ANSIBLE_MODULE_ACTIONS.get(module or "")
            if action_id:
                reason = f"module {module}"
            else:
                action_id = "telecommunications.apply_playbook_change"
                reason = (f"module {module} has no direct mapping — routed to the generic "
                          f"change applier") if module else "no module detected"

            entry = grouped.setdefault(action_id, {"count": 0, "examples": []})
            entry["count"] += 1
            if len(entry["examples"]) < 3:
                entry["examples"].append(task["name"])

            mapping.append({
                "source": task["name"],
                "source_type": f"ansible task ({play['name']})",
                "status": "MAPPED" if module in ANSIBLE_MODULE_ACTIONS else "REVIEW",
                "action_id": action_id,
                "reason": reason,
            })

    actions = [
        {
            "name": action_id.split(".")[-1],
            "action_id": action_id,
            "description": f"Covers {info['count']} task{'' if info['count'] == 1 else 's'} "
                           f"from the imported playbook",
            "required": True,
        }
        for action_id, info in grouped.items()
    ]

    rules = [
        f"Source playbook: {title}",
        f"{parsed['play_count']} play(s), {parsed['task_count']} task(s) imported",
    ]
    if parsed["roles"]:
        rules.append(f"Roles referenced: {', '.join(parsed['roles'])}")
    hosts = [p["hosts"] for p in parsed["plays"] if p.get("hosts")]
    if hosts:
        rules.append(f"Target groups: {', '.join(str(h) for h in hosts)}")

    playbook = {
        "name": slug,
        "version": "1.0.0",
        "description": f"Imported from Ansible playbook “{title}”",
        "industry": "telecommunications",
        "category": "provisioning",
        "intent": (
            f"Perform the provisioning previously handled by the Ansible playbook “{title}”. "
            f"{parsed['task_count']} tasks mapped onto {len(grouped)} Apex actions. Steps that "
            f"change hardware state remain gated on human approval."
        ),
        "output": [{
            "name": "provisioning_result",
            "type": "structured_data",
            "description": "Per-step outcome and any configuration changed",
        }],
        "context": {"business_rules": rules},
        "actions": actions,
        "recipe": "\n".join(
            [f"Imported from the Ansible playbook “{title}”.", ""]
            + [f"{i}. {aid} — {info['count']} tasks (e.g. {', '.join(info['examples'][:2])})"
               for i, (aid, info) in enumerate(grouped.items(), start=1)]
        ),
        "triggers": [{"type": "manual"}],
    }

    return {"playbook": playbook, "mapping": mapping}


# ─────────────────────────────────────────────────────────────────────────────
# orchestration
# ─────────────────────────────────────────────────────────────────────────────

def analyze(content: str, filename: str = "", name_hint: str = "") -> Dict[str, Any]:
    """
    Parse a source workflow and propose an Apex playbook.

    Writes nothing. The returned `mapping` explains every source element, so a
    reviewer can see what Apex made of their file before committing it.
    """
    fmt = detect_format(content, filename)
    warnings: List[str] = []

    if fmt == "robot_framework":
        parsed = parse_robot(content)
        built = robot_to_playbook(parsed, name_hint or Path(filename).stem)
        summary = {
            "format": "Robot Framework",
            "suite": parsed["suite_name"],
            "tests": parsed["test_count"],
            "outcomes": parsed["outcomes"],
            "libraries": parsed["libraries"],
            "metadata": parsed["metadata"],
        }
        unmapped = [l for l in parsed["libraries"] if l not in ROBOT_LIBRARY_ACTIONS]
        if unmapped:
            warnings.append(
                f"Keyword librar{'y' if len(unmapped) == 1 else 'ies'} without a direct "
                f"Apex action: {', '.join(unmapped)} — mapped by test topic instead."
            )

    elif fmt == "ansible":
        parsed = parse_ansible(content)
        built = ansible_to_playbook(parsed, name_hint or Path(filename).stem)
        summary = {
            "format": "Ansible",
            "plays": parsed["play_count"],
            "tasks": parsed["task_count"],
            "modules": parsed["modules"],
            "roles": parsed["roles"],
        }
        unmapped = [m for m in parsed["modules"] if m not in ANSIBLE_MODULE_ACTIONS]
        if unmapped:
            warnings.append(
                f"Module(s) without a direct Apex action: {', '.join(unmapped)} — "
                f"routed to the generic change applier and flagged REVIEW."
            )
        if parsed["roles"]:
            warnings.append(
                f"{len(parsed['roles'])} role(s) referenced but not expanded — "
                f"import the role task files separately for full coverage."
            )

    elif fmt == "apex_playbook":
        raise ValueError("This is already an Apex playbook — add it to playbooks/ directly.")
    else:
        raise ValueError(
            f"Unrecognised workflow format ({fmt}). Supported: Robot Framework output.xml "
            f"and Ansible playbook YAML."
        )

    review = sum(1 for m in built["mapping"] if m["status"] == "REVIEW")
    return {
        "detected_format": fmt,
        "source_summary": summary,
        "proposed_playbook": built["playbook"],
        "mapping": built["mapping"],
        "mapped_count": len(built["mapping"]),
        "review_count": review,
        "action_count": len(built["playbook"]["actions"]),
        "warnings": warnings,
        "yaml_preview": yaml.safe_dump(built["playbook"], sort_keys=False, allow_unicode=True),
    }


def commit(playbook: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
    """Write the proposed playbook to disk in the flat format the seeder expects."""
    industry = playbook.get("industry") or "telecommunications"
    slug = _slug(playbook.get("name") or "imported_playbook")
    target_dir = PLAYBOOKS_DIR / industry
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{slug}.yaml"

    if path.exists() and not overwrite:
        raise FileExistsError(f"{path.relative_to(ROOT)} already exists — pass overwrite=true to replace it")

    playbook = dict(playbook)
    playbook["name"] = slug
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(playbook, f, sort_keys=False, allow_unicode=True)

    log.info("import.committed", path=str(path), industry=industry)
    return {
        "path": str(path.relative_to(ROOT)),
        "playbook_name": slug,
        "industry": industry,
        "seed_command": (
            f"curl -X POST 'http://localhost:8002/api/v1/playbooks/seed"
            f"?industry={industry}&force=true'"
        ),
    }


def list_samples() -> List[Dict[str, Any]]:
    """Real artifacts shipped with the platform that can be imported as-is."""
    out = []
    for p in sorted(SAMPLES_DIR.glob("*.xml")):
        try:
            size = p.stat().st_size
        except OSError:
            continue
        out.append({
            "filename": p.name,
            "path": str(p.relative_to(ROOT)),
            "format": "robot_framework",
            "size_bytes": size,
            "description": _describe_sample(p.name),
        })
    return out


def read_sample(filename: str) -> str:
    """Read a shipped sample. Filename only — no path traversal."""
    safe = Path(filename).name
    path = SAMPLES_DIR / safe
    if not path.is_file():
        raise FileNotFoundError(f"No such sample: {safe}")
    return path.read_text(encoding="utf-8", errors="replace")


def _describe_sample(name: str) -> str:
    if "historical" in name:
        return "Historical CaaS node run — firmware 23.12 baseline"
    if "baseline" in name:
        return "Baseline CaaS node run — firmware 24.06"
    if "full" in name:
        return "Full CaaS node certification run — firmware 24.12"
    if "partial" in name:
        return "Partial run — suite aborted part-way"
    return "Robot Framework certification output"


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    s = re.sub(r"^robot_output_", "", s)
    return s or "imported_playbook"
