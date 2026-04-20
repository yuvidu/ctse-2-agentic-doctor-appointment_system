import ollama
import json
import re

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

Input: "{user_input}"
"""

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
    return extract_json(content)