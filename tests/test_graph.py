from skill_path.graph import route_after_guardrail


def test_route_after_guardrail_routes_all_known_states() -> None:
    assert route_after_guardrail({"guardrail_status": "PASS"}) == "pass"
    assert route_after_guardrail({"guardrail_status": "RETRY"}) == "retry"
    assert route_after_guardrail({"guardrail_status": "FAIL"}) == "fail"
