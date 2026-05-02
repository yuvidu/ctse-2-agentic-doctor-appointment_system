import ollama
import json
import re

from tools.notification_tools.logging_tool import log_event

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
    - user_name (extract full name if provided, else empty string)
    - user_contact (extract phone or email if provided, else empty string)
    - specialization
    - date
    - time_preference

    u need to match specilization to closest one from the list of available specializations. reread if you are not found specilazation.
    if you are not found date or time, retuurn tomorrow date and morning time.

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