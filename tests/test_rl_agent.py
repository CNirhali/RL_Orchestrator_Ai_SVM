from orchestrator.rl_agent import RLAgent


def test_reward_function_monotonicity():
    agent = RLAgent(state_file=":memory:")

    r_success_low_cost = agent.calculate_reward(
        success=True, cost=0.1, time_taken=1.0, lint_errors=0
    )
    r_success_high_cost = agent.calculate_reward(
        success=True, cost=10.0, time_taken=1.0, lint_errors=0
    )
    assert r_success_low_cost > r_success_high_cost

    r_success = agent.calculate_reward(success=True, cost=0.1, time_taken=1.0, lint_errors=0)
    r_fail = agent.calculate_reward(success=False, cost=0.1, time_taken=1.0, lint_errors=0)
    assert r_success > r_fail

