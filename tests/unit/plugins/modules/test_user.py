import pytest
import json
from unittest.mock import patch, MagicMock

import plugins.modules.user as user_module

def test_user_get(monkeypatch):
    # Mock subprocess.run to return a fake user JSON
    fake_output = json.dumps({"id": 1, "login": "jdoe"})
    mock_run = MagicMock()
    mock_run.return_value.stdout = fake_output
    monkeypatch.setattr(user_module.subprocess, "run", lambda *a, **kw: mock_run.return_value)

    # Mock AnsibleModule
    class DummyModule:
        def __init__(self):
            self.params = {
                "state": "get",
                "user_id": 1,
                "api_url": "fake",
                "username": "fake",
                "password_api": "fake"
            }
        def exit_json(self, **kwargs):
            self.results = kwargs
            raise SystemExit
        def fail_json(self, **kwargs):
            raise Exception(kwargs)

    module = DummyModule()
    with pytest.raises(SystemExit):
        user_module.run_module.__globals__["AnsibleModule"] = lambda **kwargs: module
        user_module.run_module()
    assert module.results["user"]["id"] == 1
    assert module.results["user"]["login"] == "jdoe"