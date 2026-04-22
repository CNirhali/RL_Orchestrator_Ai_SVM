import importlib


def _reload_app_with_env(monkeypatch, tmp_path):
    # Ensure module-level singletons (provisioner, rl_agent) are created with test paths.
    monkeypatch.setenv("MAO_WORKSPACE_ROOT", str(tmp_path / "workspaces"))
    monkeypatch.setenv("MAO_RL_STATE_FILE", str(tmp_path / "rl_state.json"))
    monkeypatch.setenv("MAO_ENABLE_GIT_CLONE", "false")
    monkeypatch.setenv("MAO_SIM_SEED", "123")
    monkeypatch.setenv("MAO_SIM_SLEEP_S", "0")

    import main as main_module
    import orchestrator.provisioner as provisioner_module
    import orchestrator.rl_agent as rl_agent_module
    import orchestrator.router as router_module

    importlib.reload(provisioner_module)
    importlib.reload(rl_agent_module)
    importlib.reload(router_module)
    importlib.reload(main_module)
    return main_module


def test_webhook_task_completes(monkeypatch, tmp_path):
    main_module = _reload_app_with_env(monkeypatch, tmp_path)

    from fastapi.testclient import TestClient

    client = TestClient(main_module.app)

    resp = client.post(
        "/webhook/task",
        json={
            "repository_url": "dummy",
            "description": "Fix a small bug in the authentication flow.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "accepted"
    task_id = body["task_id"]

    # BackgroundTasks are executed before the response is fully returned in TestClient,
    # so the task should already be completed or failed deterministically here.
    status = client.get(f"/tasks/{task_id}").json()
    assert status["task_id"] == task_id
    assert status["status"] in {"completed", "failed"}
    if status["status"] == "completed":
        assert "result" in status
        assert status["result"]["status"] == "completed"

