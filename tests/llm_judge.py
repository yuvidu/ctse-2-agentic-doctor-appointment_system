import ollama

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
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]