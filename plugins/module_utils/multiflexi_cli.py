# -*- coding: utf-8 -*-
"""Shared helpers for read-only ``*_info`` modules that wrap ``multiflexi-cli``."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re
import subprocess

# Field names whose values are secrets; masked in *_info results unless show_secrets=true.
SECRET_KEY = re.compile(r"(pass(word|wd)?|secret|api[_-]?key|private[_-]?key|^token(_value)?$|_token$)", re.I)
MASK = "***"

COMMON_LIST_ARGS = dict(
    limit=dict(type="int", required=False),
    offset=dict(type="int", required=False),
    order=dict(type="str", required=False, choices=["A", "D"]),
    fields=dict(type="list", elements="str", required=False),
    show_secrets=dict(type="bool", required=False, default=False),
    multiflexi_cli_path=dict(type="str", required=False, default="multiflexi-cli"),
)


def run_cli_json(module, args):
    """Run ``multiflexi-cli <args> --format json`` and return the parsed JSON.

    A non-zero exit code is tolerated when stdout still holds JSON (the CLI
    reports ``{"status": "not found"}`` that way); otherwise the task fails.
    """
    cmd = [module.params.get("multiflexi_cli_path") or "multiflexi-cli"] + args + ["--format", "json"]
    if module._verbosity >= 2:
        module.warn("Running CLI command: %s" % " ".join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        module.fail_json(msg="Failed to run %s: %s" % (cmd[0], exc))
    if module._verbosity >= 2:
        module.warn("CLI stdout: %s" % result.stdout.strip())
        if result.stderr.strip():
            module.warn("CLI stderr: %s" % result.stderr.strip())
    try:
        return json.loads(result.stdout)
    except ValueError:
        if result.returncode != 0:
            module.fail_json(msg="multiflexi-cli error: %s" % (result.stderr.strip() or result.stdout.strip()), rc=result.returncode)
        module.fail_json(msg="multiflexi-cli returned invalid JSON: %s" % result.stdout.strip()[:200])


def _mask_json_string(text):
    """Redact secrets inside a string that holds a JSON object or list; other strings are returned unchanged."""
    stripped = text.strip()
    if stripped[:1] in ("{", "[") and stripped[-1:] in ("}", "]"):
        try:
            decoded = json.loads(stripped)
        except ValueError:
            return text
        redacted = redact(decoded)
        return json.dumps(redacted) if redacted != decoded else text
    return text


LABEL_KEYS = ("name", "key", "field", "keyword")


def _is_secret_label(text):
    return bool(SECRET_KEY.search(re.sub(r"[\s-]+", "_", text.strip().lower())))


def redact(value):
    """Return a copy of value with the content of secret-looking fields masked (recursive).

    Besides fields whose *name* looks secret this also masks name/value records
    (``{"name": "password", "value": "...", "default": "..."}``): when any label field
    (name, key, field, keyword) of a record names a secret, every other non-empty scalar of
    the record is masked. Secrets inside JSON-encoded strings are masked too.
    """
    if isinstance(value, dict):
        labelled = any(isinstance(value.get(k), str) and _is_secret_label(value[k]) for k in LABEL_KEYS)
        out = {}
        for k, v in value.items():
            if v in (None, ""):
                out[k] = v
            elif SECRET_KEY.search(str(k)):
                out[k] = MASK
            elif labelled and k not in LABEL_KEYS and isinstance(v, (str, int, float)) and not isinstance(v, bool):
                out[k] = MASK
            else:
                out[k] = redact(v)
        return out
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return _mask_json_string(value)
    return value


def project(value, safe_fields):
    """Keep only the allowlisted fields of each record (used for entities that mostly hold secrets)."""
    if not safe_fields:
        return value
    if isinstance(value, list):
        return [project(v, safe_fields) for v in value]
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if k in safe_fields}
    return value


def _is_not_found(data):
    return isinstance(data, dict) and str(data.get("status", "")).lower() in ("not found", "not_found")


def _fail_on_error(module, data):
    if isinstance(data, dict) and str(data.get("status", "")).lower() == "error":
        module.fail_json(msg="multiflexi-cli error: %s" % data.get("message", data))


def _rows(data):
    """Normalise a list response to a list of dicts."""
    if data is None:
        return []
    if isinstance(data, dict):
        for key in ("items", "data", "results"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data] if data else []
    return list(data)


def info_argument_spec(selectors=None, filters=None):
    """Build an argument_spec: selectors (get by key), filters (list filters) and paging options."""
    spec = dict(COMMON_LIST_ARGS)
    for name, kind in (selectors or {}).items():
        spec[name] = dict(type=kind, required=False)
    for name, kind in (filters or {}).items():
        spec[name] = dict(type=kind, required=False)
    return spec


def run_info(module, singular, plural, list_command, get_command=None, selectors=None, filters=None, safe_fields=None):
    """Execute an info module.

    ``selectors`` maps module params to ``<get_command>`` CLI options (``{"id": "--id"}``).
    The first one given is used to fetch a single record; with none given the whole list is returned.
    ``filters`` maps module params to ``<list_command>`` CLI options.
    ``safe_fields`` is an allowlist of fields returned unless ``show_secrets`` is set (for entities that hold secrets).
    """
    params = module.params
    if get_command:
        for name, option in (selectors or {}).items():
            if params.get(name) is not None:
                args = [get_command, option, str(params[name])]
                if params.get("fields"):
                    args += ["--fields", ",".join(params["fields"])]
                data = run_cli_json(module, args)
                _fail_on_error(module, data)
                if _is_not_found(data) or not data:
                    module.exit_json(changed=False, found=False, **{singular: None})
                if not params.get("show_secrets"):
                    data = redact(project(data, safe_fields))
                module.exit_json(changed=False, found=True, **{singular: data})

    args = [list_command]
    for name, option in (filters or {}).items():
        if params.get(name) is not None:
            args += [option, str(params[name])]
    for name in ("limit", "offset", "order"):
        if params.get(name) is not None:
            args += ["--%s" % name, str(params[name])]
    if params.get("fields"):
        args += ["--fields", ",".join(params["fields"])]
    data = run_cli_json(module, args)
    _fail_on_error(module, data)
    if _is_not_found(data):
        data = []
    rows = _rows(data)
    if not params.get("show_secrets"):
        rows = redact(project(rows, safe_fields))
    module.exit_json(changed=False, count=len(rows), **{plural: rows})
