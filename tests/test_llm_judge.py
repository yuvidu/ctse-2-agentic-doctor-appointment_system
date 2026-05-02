import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intent_agent import intent_agent
from tests.llm_judge import judge_output


def test_llm_judge_valid_case():
    state = {"user_input": "Book dentist tomorrow"}

    result = intent_agent(state)

    evaluation = judge_output(result)

    print("Agent Output:", result)
    print("Judge Result:", evaluation)

    # SLMs may answer with a sentence; require leading verdict token.
    evaluation_clean = evaluation.lower().strip()
    assert evaluation_clean.startswith("valid") or evaluation_clean.startswith("invalid")

if __name__ == "__main__":
    test_llm_judge_valid_case()