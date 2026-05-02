import os

import ollama

_JUDGE_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")


def judge_output(output: dict) -> str:

    prompt = f"""
You are a strict evaluator.

Check if this output is valid for a medical booking system:

Rules:
- Must contain specialization
- Must be structured JSON
- Must NOT contain hallucinated data

Output:
{output}

Answer ONLY: valid or invalid
"""

    response = ollama.chat(
        model=_JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]