import importlib.util
import json
import pathlib
from unittest import mock

import pytest

spec = importlib.util.spec_from_file_location(
    "multiflexi_cli_utils",
    pathlib.Path(__file__).parents[2] / "plugins/module_utils/multiflexi_cli.py",
)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class Exit(Exception):
    def __init__(self, **kw):
        self.kw = kw


class Fail(Exit):
    pass


def make_module(**params):
    m = mock.Mock()
    m._verbosity = 0
    m.params = dict(multiflexi_cli_path="multiflexi-cli", **params)
    m.exit_json.side_effect = lambda **kw: (_ for _ in ()).throw(Exit(**kw))
    m.fail_json.side_effect = lambda **kw: (_ for _ in ()).throw(Fail(**kw))
    return m


def proc(stdout="", returncode=0, stderr=""):
    return mock.Mock(stdout=stdout, returncode=returncode, stderr=stderr)


def run(module, **kw):
    with pytest.raises(Exit) as exc:
        cli.run_info(module, **kw)
    return exc.value


def test_list_passes_filters_and_paging():
    m = make_module(status="failed", limit=5, offset=None, order="D", fields=["id", "status"])
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps([{"id": 9}]))) as sp:
        out = run(m, singular="job", plural="jobs", list_command="job:list", get_command="job:get",
                  selectors={"id": "--id"}, filters={"status": "--status"})
    assert sp.call_args[0][0] == ["multiflexi-cli", "job:list", "--status", "failed", "--limit", "5",
                                  "--order", "D", "--fields", "id,status", "--format", "json"]
    assert out.kw == dict(changed=False, count=1, jobs=[{"id": 9}])


def test_selector_fetches_single_record():
    m = make_module(uuid="u-1")
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps({"id": 1}))) as sp:
        out = run(m, singular="application", plural="applications", list_command="application:list",
                  get_command="application:get", selectors={"id": "--id", "uuid": "--uuid"})
    assert sp.call_args[0][0] == ["multiflexi-cli", "application:get", "--uuid", "u-1", "--format", "json"]
    assert out.kw == dict(changed=False, found=True, application={"id": 1})


def test_not_found_is_null_even_with_nonzero_rc():
    m = make_module(id=7)
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps({"status": "not found"}), returncode=1)):
        out = run(m, singular="job", plural="jobs", list_command="job:list", get_command="job:get", selectors={"id": "--id"})
    assert out.kw == dict(changed=False, found=False, job=None)


def test_error_status_fails():
    m = make_module()
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps({"status": "error", "message": "boom"}), returncode=2)):
        with pytest.raises(Fail):
            cli.run_info(m, singular="user", plural="users", list_command="user:list")


def test_invalid_json_with_failure_fails():
    m = make_module()
    with mock.patch.object(cli.subprocess, "run", return_value=proc("not json", returncode=3, stderr="bad")):
        with pytest.raises(Fail):
            cli.run_info(m, singular="user", plural="users", list_command="user:list")


def test_wrapped_list_response_is_unwrapped():
    m = make_module()
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps({"items": [{"id": 1}, {"id": 2}]}))):
        out = run(m, singular="user", plural="users", list_command="user:list")
    assert out.kw["count"] == 2


def test_secrets_are_masked_by_default():
    m = make_module()
    rows = [{"id": 1, "token": "abc", "user_id": 3, "cfg": {"db_password": "x", "host": "h"}, "api_key": "", "executable": "/bin/x"}]
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps(rows))):
        out = run(m, singular="token", plural="tokens", list_command="token:list")
    rec = out.kw["tokens"][0]
    assert rec["token"] == "***" and rec["cfg"]["db_password"] == "***"
    assert rec["cfg"]["host"] == "h" and rec["user_id"] == 3 and rec["executable"] == "/bin/x"
    assert rec["api_key"] == ""  # empty secrets are left alone


def test_show_secrets_returns_raw_values():
    m = make_module(show_secrets=True)
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps([{"id": 1, "token": "abc"}]))):
        out = run(m, singular="token", plural="tokens", list_command="token:list")
    assert out.kw["tokens"] == [{"id": 1, "token": "abc"}]


def test_single_record_is_masked_too():
    m = make_module(id=1)
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps({"id": 1, "password": "p"}))):
        out = run(m, singular="user", plural="users", list_command="user:list", get_command="user:get", selectors={"id": "--id"})
    assert out.kw["user"] == {"id": 1, "password": "***"}


def test_name_value_records_are_masked():
    rows = [{"name": "password", "value": "hunter2"}, {"name": "host", "value": "db1"}]
    assert cli.redact(rows) == [{"name": "password", "value": "***"}, {"name": "host", "value": "db1"}]


def test_json_encoded_strings_are_redacted():
    out = cli.redact({"config": '{"db_password": "x", "host": "h"}', "note": "plain {text}"})
    assert json.loads(out["config"]) == {"db_password": "***", "host": "h"}
    assert out["note"] == "plain {text}"


def test_safe_fields_allowlist_drops_everything_else():
    m = make_module()
    rows = [{"id": 1, "name": "c", "company_id": 2, "payload": "opaque-secret"}]
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps(rows))):
        out = run(m, singular="credential", plural="credentials", list_command="credential:list",
                  safe_fields=["id", "name", "company_id"])
    assert out.kw["credentials"] == [{"id": 1, "name": "c", "company_id": 2}]


def test_safe_fields_not_applied_with_show_secrets():
    m = make_module(show_secrets=True)
    with mock.patch.object(cli.subprocess, "run", return_value=proc(json.dumps([{"id": 1, "payload": "x"}]))):
        out = run(m, singular="credential", plural="credentials", list_command="credential:list", safe_fields=["id"])
    assert out.kw["credentials"] == [{"id": 1, "payload": "x"}]


def test_any_label_key_marks_record_secret():
    rec = {"field": "API-Key", "name": "display", "value": "v", "default": "d", "defval": 5, "enabled": True}
    out = cli.redact(rec)
    assert out == {"field": "API-Key", "name": "display", "value": "***", "default": "***", "defval": "***", "enabled": True}


def test_label_normalisation_and_non_secret_records_untouched():
    assert cli.redact({"key": "DB Password", "value": "x"})["value"] == "***"
    assert cli.redact({"key": "client-secret", "value": "x"})["value"] == "***"
    assert cli.redact({"name": "host", "key": "db", "value": "h", "default": "d"}) == {"name": "host", "key": "db", "value": "h", "default": "d"}
