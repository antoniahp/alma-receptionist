

def test_an_action_sent_as_plain_text_does_not_break_the_chat():
    from domain.entities.ai_decision import AiDecision

    assert AiDecision.from_dict({"reply": "Te paso con Cris", "action": "handoff"}).action == "handoff"
    assert AiDecision.from_dict({"reply": "Hola", "action": ["raro"]}).action == "none"
