import importlib.util
import json
import pathlib
from unittest import mock

import pytest

MODULES = pathlib.Path(__file__).parents[2] / "plugins/modules"


def load(name):
    spec = importlib.util.spec_from_file_location(name, MODULES / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


eventsource = load("eventsource")
eventrule = load("eventrule")


class Exit(Exception):
    def __init__(self, **kw):
        self.kw = kw


class Fail(Exit):
    pass


def fake_ansible_module(params):
    """Return a factory replacing AnsibleModule with a controllable stand-in."""
    full = dict(multiflexi_cli_path="multiflexi-cli", **params)

    def factory(argument_spec=None, supports_check_mode=False):
        m = mock.Mock()
        m.params = {k: None for k in (argument_spec or {})}
        m.params.update(full)
        m.check_mode = False
        m.exit_json.side_effect = lambda **kw: (_ for _ in ()).throw(Exit(**kw))
        m.fail_json.side_effect = lambda **kw: (_ for _ in ()).throw(Fail(**kw))
        return m

    return factory


def run_module(mod, params, cli_outputs):
    """Run mod.run_module() with scripted CLI output; returns (result, commands)."""
    commands = []

    def fake_cli(args):
        commands.append(args[1:])
        out = cli_outputs(args[1:])
        if isinstance(out, Exception):
            raise out
        return out

    with mock.patch.object(mod, "AnsibleModule", fake_ansible_module(params)), \
            mock.patch.object(mod, "run_cli_command", side_effect=fake_cli):
        with pytest.raises(Exit) as exc:
            mod.run_module()
    return exc.value, commands


EXISTING_SOURCE = {"id": 7, "name": "Acceptor", "adapter_type": "abraflexi-webhook-acceptor",
                   "db_connection": "mysql", "db_host": "localhost", "db_port": "3306",
                   "db_database": "db", "db_username": "u", "db_password": "p",
                   "enabled": 1, "poll_interval": 60}


def source_cli(args):
    if args[0] == "event-source:list":
        return json.dumps([EXISTING_SOURCE])
    if args[0] == "event-source:get":
        return json.dumps(EXISTING_SOURCE)
    raise AssertionError(f"unexpected CLI call {args}")


def test_eventsource_present_reuses_existing_by_name_and_is_unchanged():
    out, cmds = run_module(eventsource, dict(state="present", name="Acceptor", adapter_type="abraflexi-webhook-acceptor",
                                             db_connection="mysql", db_host="localhost", db_port="3306",
                                             db_database="db", db_username="u", db_password="p", enabled=True),
                           source_cli)
    assert not isinstance(out, Fail)
    assert out.kw.get("changed") in (False, None)
    assert not any(c[0] == "event-source:create" for c in cmds)


def test_eventsource_present_creates_when_name_unknown():
    def cli(args):
        if args[0] == "event-source:list":
            return "[]"
        if args[0] == "event-source:create":
            return json.dumps({"id": 8})
        raise AssertionError(args)

    out, cmds = run_module(eventsource, dict(state="present", name="New"), cli)
    assert out.kw["changed"] is True
    assert any(c[0] == "event-source:create" for c in cmds)


def test_eventsource_cli_error_is_reported_not_a_msg_collision():
    def cli(args):
        return Exception("multiflexi-cli error: boom")

    out, _ = run_module(eventsource, dict(state="present", name="X"), cli)
    assert isinstance(out, Fail)
    assert out.kw["msg"] == "multiflexi-cli error: boom"


RULE = dict(state="present", eventsource_id=1, runtemplate_id=5, evidence="faktura-vydana",
            operation="settled", env_mapping='{"INVOICE_ID": "recordid"}', enabled=True)
EXISTING_RULE = {"id": 3, "event_source_id": 1, "runtemplate_id": 5, "evidence": "faktura-vydana",
                 "operation": "settled", "env_mapping": {"INVOICE_ID": "recordid"}, "enabled": 1}


def test_eventrule_present_is_idempotent():
    def cli(args):
        if args[0] == "event-rule:list":
            return json.dumps([EXISTING_RULE])
        if args[0] == "event-rule:get":
            return json.dumps(EXISTING_RULE)
        raise AssertionError(args)

    out, cmds = run_module(eventrule, dict(RULE), cli)
    assert not isinstance(out, Fail)
    assert out.kw.get("changed") in (False, None)
    assert not any(c[0] in ("event-rule:create", "event-rule:update") for c in cmds)


def test_eventrule_updates_only_when_something_differs():
    def cli(args):
        if args[0] == "event-rule:list":
            return json.dumps([EXISTING_RULE])
        if args[0] == "event-rule:get":
            return json.dumps(EXISTING_RULE)
        if args[0] == "event-rule:update":
            return "{}"
        raise AssertionError(args)

    out, cmds = run_module(eventrule, dict(RULE, enabled=False), cli)
    assert out.kw["changed"] is True
    update = next(c for c in cmds if c[0] == "event-rule:update")
    assert "--enabled" in update and "--operation" not in update


def test_eventrule_creates_when_no_match():
    def cli(args):
        if args[0] == "event-rule:list":
            return "[]"
        if args[0] == "event-rule:create":
            return json.dumps({"id": 4})
        raise AssertionError(args)

    out, cmds = run_module(eventrule, dict(RULE), cli)
    assert out.kw["changed"] is True
    assert any(c[0] == "event-rule:create" for c in cmds)
