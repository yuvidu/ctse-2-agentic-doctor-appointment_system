import ollama
import json
import re

from tests.logging_tool import log_event

def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return {}
    return {}

def llm_parse_input(user_input: str) -> dict:
    prompt = f"""
    Extract the following fields from user input:
    - specialization
    - date
    - time_preference

    Return ONLY JSON.

    Input: "{user_input}" """

    log_event("parsing_tool", "llm_call_start_with_this_input", user_input)

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": "You ONLY return valid JSON. No explanations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response['message']['content']
    log_event("parsing_tool", "llm_raw_output", content)

    return extract_json(content)