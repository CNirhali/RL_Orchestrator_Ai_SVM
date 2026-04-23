from orchestrator.test_suite_graph import create_best_suite


def test_create_best_suite_high_risk_selects_e2e():
    result = create_best_suite(
        changed_paths=["orchestrator/router.py", "main.py"],
        run_commands=False,
    )
    assert result["risk_level"] == "high"
    assert result["suites"] == ["smoke", "core", "api_e2e"]
    assert len(result["commands"]) == 3


def test_create_best_suite_low_risk_selects_smoke_only():
    result = create_best_suite(changed_paths=["README.md"], run_commands=False)
    assert result["risk_level"] == "low"
    assert result["suites"] == ["smoke"]
    assert len(result["commands"]) == 1

