def infer_intent(query: str):
    q = query.lower()
    hard = any(k in q for k in ["python", "java", "sql", "javascript"])
    soft = any(k in q for k in ["collaborat", "stakeholder", "team"])
    cognitive = "cognitive" in q

    desired = []
    if hard:
        desired.append("Knowledge & Skills")
    if soft:
        desired.extend(["Personality & Behavior", "Competencies"])
    if cognitive:
        desired.append("Ability & Aptitude")

    return {
        "desired_test_types": list(set(desired)),
        "must_balance": hard and soft
    }
