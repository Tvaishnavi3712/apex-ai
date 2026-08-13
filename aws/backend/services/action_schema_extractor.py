"""
Action Schema Extractor
----------------------

Reads action handler files from disk and extracts their real input/output
schemas WITHOUT importing/executing the module. We use AST analysis so we
don't need to resolve the handler's boto3 / AWS dependencies just to learn
its schema.

Three extraction strategies are tried in order; the first that yields any
fields wins:

1. **Decorator extraction** — parse the `@apex_action(ApexActionSchema(...))`
   decorator call. We walk the `input_schema=...` and `output_schema=...`
   keyword arguments, following the `.add_string(...)` / `.add_number(...)`
   builder chain to recover each field's name, type, description, required.
   This is the richest source when present.

2. **Docstring extraction** — parse Google-style `Args:` / `Returns:` or
   Apex-style `Input:` / `Output:` sections in the handler function's
   docstring. Types are inferred from simple field-name heuristics.

3. **Return-dict extraction** — scan for `return {...}` literal dict
   expressions in the function body and collect their keys as output
   fields. Used as a last resort for output when neither a decorator nor
   a well-formed docstring is present.

Public API:

    extract_schemas(handler_file: str, action_name: str) -> tuple[dict, dict]

Returns `(input_schema, output_schema)` where each schema is a
`{field_name: {"type": "...", "description": "...", "required": bool}}`
mapping. If extraction fails entirely (unreadable file, syntax error, etc.)
both schemas are empty dicts — the caller decides how to present that.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Schema = Dict[str, Dict[str, Any]]
SchemaPair = Tuple[Schema, Schema]

# Map the SDK's builder method names to JSON Schema types.
_BUILDER_TYPE_MAP = {
    "add_string": "string",
    "add_number": "number",
    "add_integer": "integer",
    "add_boolean": "boolean",
    "add_array": "array",
    "add_object": "object",
}

# Heuristic field-name → type fallback for docstring extraction (no explicit type).
# Ordered: more specific patterns first.
_TYPE_HINTS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^(is_|has_|can_|should_)"),                    "boolean"),
    (re.compile(r"(_complete|_enabled|_valid|_matched|_found)$"), "boolean"),
    (re.compile(r"(_items|_list|_codes|_results|_errors|s)$"),    "array"),
    (re.compile(r"(_data|_map|_config|_context|_scores|_metadata)$"), "object"),
    (re.compile(r"(_count|_amount|_total|_price|_rate|_pct|_percent|_score|_id|_number)$"), "number"),
    (re.compile(r"^(amount|count|total|price|rate|score)$"),      "number"),
]


def extract_schemas(handler_file: str, action_name: str) -> SchemaPair:
    """Extract (input_schema, output_schema) from an action handler file.

    Returns ({}, {}) if the file is unreadable or unparseable.
    """
    try:
        source = Path(handler_file).read_text(encoding="utf-8")
    except Exception:
        return {}, {}

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}, {}

    # Find the function that matches the action name (case-insensitive).
    target_fn = _find_target_function(tree, action_name)
    if target_fn is None:
        return {}, {}

    # Strategy 1 — decorator
    input_schema, output_schema = _extract_from_decorator(target_fn)
    if input_schema or output_schema:
        # Fill in output from return dict if decorator only declared input.
        if not output_schema:
            output_schema = _extract_from_return_dicts(target_fn)
        return input_schema, output_schema

    # Strategy 2 — docstring
    docstring = ast.get_docstring(target_fn) or ""
    input_schema, output_schema = _extract_from_docstring(docstring)
    if not output_schema:
        # Strategy 3 — return-dict fallback for output only
        output_schema = _extract_from_return_dicts(target_fn)

    return input_schema, output_schema


# ─────────────────── function discovery ───────────────────

def _find_target_function(tree: ast.Module, action_name: str) -> Optional[ast.FunctionDef]:
    """Find the function most likely to be the action's entry point.

    Preference order:
      1. Function whose name matches `action_name` exactly.
      2. First function decorated with @apex_action.
      3. First async def in the module.
      4. First non-underscore, non-private def in the module.
    """
    all_funcs = [
        n for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    # 1. Exact name match
    for fn in all_funcs:
        if fn.name == action_name:
            return fn  # type: ignore[return-value]

    # 2. Decorated with @apex_action
    for fn in all_funcs:
        for dec in fn.decorator_list:
            if _decorator_is_apex_action(dec):
                return fn  # type: ignore[return-value]

    # 3. First async def
    for fn in all_funcs:
        if isinstance(fn, ast.AsyncFunctionDef):
            return fn  # type: ignore[return-value]

    # 4. First public def
    for fn in all_funcs:
        if not fn.name.startswith("_"):
            return fn  # type: ignore[return-value]

    return None


def _decorator_is_apex_action(dec: ast.AST) -> bool:
    """`@apex_action(...)` or `@sdk.apex_action(...)`."""
    call = dec if isinstance(dec, ast.Call) else None
    if not call:
        return False
    func = call.func
    if isinstance(func, ast.Name) and func.id == "apex_action":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "apex_action":
        return True
    return False


# ─────────────────── strategy 1: decorator ───────────────────

def _extract_from_decorator(fn: ast.AST) -> SchemaPair:
    """Walk @apex_action(ApexActionSchema(input_schema=..., output_schema=...))."""
    input_schema: Schema = {}
    output_schema: Schema = {}

    for dec in getattr(fn, "decorator_list", []):
        if not _decorator_is_apex_action(dec):
            continue
        # The first positional arg should be an ApexActionSchema(...) call.
        if not isinstance(dec, ast.Call) or not dec.args:
            continue
        schema_call = dec.args[0]
        if not isinstance(schema_call, ast.Call):
            continue

        for kw in schema_call.keywords:
            if kw.arg == "input_schema":
                input_schema = _parse_schema_builder(kw.value)
            elif kw.arg == "output_schema":
                output_schema = _parse_schema_builder(kw.value)

    return input_schema, output_schema


def _parse_schema_builder(node: ast.AST) -> Schema:
    """Given `ActionInputSchema(...).add_string("x", "desc", required=True).add_number(...)`,
    walk the call chain from tail to head and collect each `.add_*` call.
    """
    schema: Schema = {}

    # Recursively walk the builder chain. `node` is the outermost Call.
    calls: List[ast.Call] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Call):
        calls.append(cur)
        # Walk down the receiver: node.func is Attribute(value=<inner_call>, attr=...)
        if isinstance(cur.func, ast.Attribute):
            cur = cur.func.value
        else:
            break

    # Calls are innermost-first in the tail, outermost-first is what we collected.
    # Reverse so that the order matches declaration order in the source.
    for call in reversed(calls):
        if not isinstance(call.func, ast.Attribute):
            continue
        method = call.func.attr
        json_type = _BUILDER_TYPE_MAP.get(method)
        if not json_type:
            continue

        # Extract: (name, description, required?)
        name = _literal_str(call.args[0]) if len(call.args) >= 1 else None
        description = _literal_str(call.args[1]) if len(call.args) >= 2 else ""
        required = False
        for kw in call.keywords:
            if kw.arg == "required":
                required = _literal_bool(kw.value) or False
            elif kw.arg == "description" and not description:
                description = _literal_str(kw.value) or ""

        if not name:
            continue

        schema[name] = {
            "type": json_type,
            "description": description,
            "required": required,
        }

    return schema


def _literal_str(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _literal_bool(node: ast.AST) -> Optional[bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


# ─────────────────── strategy 2: docstring ───────────────────

# Matches both Google-style ("Args:") and Apex-style ("Input:") section headers.
_SECTION_HEADER_RE = re.compile(
    r"^\s*(Args|Arguments|Parameters|Input|Inputs|Returns|Return|Output|Outputs|Yields|Raises|Example|Examples|Notes?)\s*:\s*$",
    re.IGNORECASE,
)

# "    field_name (type, optional): Description." — type is optional.
_FIELD_LINE_RE = re.compile(
    r"""^
    \s+                               # indented
    (?P<name>[a-zA-Z_][a-zA-Z0-9_]*)  # identifier
    \s*
    (?:\((?P<type>[^)]+)\))?          # optional (type[, modifier])
    \s*:\s*
    (?P<desc>.+?)\s*$
    """,
    re.VERBOSE,
)


def _extract_from_docstring(docstring: str) -> SchemaPair:
    if not docstring:
        return {}, {}

    input_schema: Schema = {}
    output_schema: Schema = {}

    current_section: Optional[str] = None
    lines = docstring.splitlines()

    for line in lines:
        # Detect section headers.
        header = _SECTION_HEADER_RE.match(line)
        if header:
            section = header.group(1).lower()
            if section in ("args", "arguments", "parameters", "input", "inputs"):
                current_section = "input"
            elif section in ("returns", "return", "output", "outputs", "yields"):
                current_section = "output"
            else:
                current_section = None
            continue

        if current_section is None:
            continue

        m = _FIELD_LINE_RE.match(line)
        if not m:
            continue

        name = m.group("name")
        raw_type = (m.group("type") or "").strip().lower()
        desc = m.group("desc").strip()

        declared_type = _docstring_type_to_json_type(raw_type)
        json_type = declared_type or _infer_type_from_name(name)

        required = False
        if "optional" in raw_type:
            required = False
        elif "required" in raw_type:
            required = True
        elif current_section == "input":
            # Google convention: absence of "optional" usually means required.
            required = True

        entry = {
            "type": json_type,
            "description": desc,
            "required": required if current_section == "input" else False,
        }

        if current_section == "input":
            input_schema[name] = entry
        else:
            output_schema[name] = entry

    return input_schema, output_schema


def _docstring_type_to_json_type(raw_type: str) -> Optional[str]:
    """Map a docstring type hint like 'str', 'float, optional', 'List[str]' to a JSON type."""
    if not raw_type:
        return None
    t = raw_type.lower()
    if "str" in t:
        return "string"
    if "bool" in t:
        return "boolean"
    if "int" in t:
        return "integer"
    if "float" in t or "decimal" in t or "number" in t:
        return "number"
    if "list" in t or "tuple" in t or "array" in t or "[" in t and "]" in t:
        return "array"
    if "dict" in t or "object" in t or "map" in t:
        return "object"
    return None


def _infer_type_from_name(name: str) -> str:
    lower = name.lower()
    for pattern, t in _TYPE_HINTS:
        if pattern.search(lower):
            return t
    return "string"


# ─────────────────── strategy 3: return-dict ───────────────────

def _extract_from_return_dicts(fn: ast.AST) -> Schema:
    """Find `return {...}` literals in the function body and collect keys.

    Returns a schema with inferred types. Keys found in any return statement are
    merged; later returns override earlier for conflicting field descriptions
    (we don't have any, so this is safe).
    """
    schema: Schema = {}

    for node in ast.walk(fn):
        if not isinstance(node, ast.Return) or node.value is None:
            continue
        if not isinstance(node.value, ast.Dict):
            continue

        for key_node, value_node in zip(node.value.keys, node.value.values):
            key = _literal_str(key_node)
            if not key or key in schema:
                continue
            schema[key] = {
                "type": _infer_type_from_ast_value(value_node, key),
                "description": "",
                "required": False,
            }

    return schema


def _infer_type_from_ast_value(node: ast.AST, name: str) -> str:
    """Guess a JSON type from the AST of the value being returned."""
    if isinstance(node, ast.Constant):
        v = node.value
        if isinstance(v, bool):
            return "boolean"
        if isinstance(v, int):
            return "integer"
        if isinstance(v, float):
            return "number"
        if isinstance(v, str):
            return "string"
        if v is None:
            return _infer_type_from_name(name)
    if isinstance(node, ast.List) or isinstance(node, ast.Tuple):
        return "array"
    if isinstance(node, ast.Dict):
        return "object"
    if isinstance(node, ast.Call):
        # len(...) → integer, float(...) → number, str(...) → string, bool(...) → boolean
        if isinstance(node.func, ast.Name):
            fn_name = node.func.id
            if fn_name in ("len",): return "integer"
            if fn_name in ("float",): return "number"
            if fn_name in ("int",): return "integer"
            if fn_name in ("str",): return "string"
            if fn_name in ("bool",): return "boolean"
            if fn_name in ("list", "sorted", "filter", "map"): return "array"
            if fn_name in ("dict",): return "object"
    return _infer_type_from_name(name)
