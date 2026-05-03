import json
import os
import re
from datetime import date, datetime

import ollama

from tools.intent_tools.date_resolve import merge_dateparser_date
from utils.logging_utils import log_event

def extract_json(text: str) -> dict[str, object]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {}
    return {}


def _apply_explicit_iso_date_from_user(user_input: str, data: dict) -> dict:
    """If the user typed exactly one YYYY-MM-DD, trust it over the SLM date (fixes off-by-one hallucinations)."""
    found = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", user_input)
    unique = list(dict.fromkeys(found))
    if len(unique) != 1:
        return data
    explicit = unique[0]
    out = dict(data)
    if out.get("date") != explicit:
        out["date"] = explicit
    return out


def _drop_hallucinated_past_date(user_input: str, data: dict) -> dict:
    """Remove a parsed date strictly before today unless the user typed that YYYY-MM-DD themselves."""
    found = set(re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", user_input))
    dval = data.get("date")
    if not isinstance(dval, str) or not dval.strip():
        return data
    dstr = dval.strip()[:10]
    if dstr in found:
        return data
    try:
        parsed_d = datetime.strptime(dstr, "%Y-%m-%d").date()
    except ValueError:
        return data
    if parsed_d >= date.today():
        return data
    out = dict(data)
    out.pop("date", None)
    return out


def llm_parse_input(user_input: str) -> dict:
    today = date.today()
    today_iso = today.isoformat()
    weekday = today.strftime("%A")
    prompt = f"""
    Extract these fields as JSON keys: specialization, date, time_preference.

    Context: today is {weekday}, {today_iso} (use this to resolve "today", "tomorrow", "next Tuesday", etc.).

    Rules:
    - Map specialization to the closest valid medical specialty name (title case is OK).
    - For "date": if the user gives a calendar date as YYYY-MM-DD anywhere in the text, copy that string EXACTLY — never change the day or substitute "tomorrow".
    - Otherwise resolve relative dates to YYYY-MM-DD on or after {today_iso}.
    - If there is truly no date in the message, use tomorrow's date as YYYY-MM-DD and time_preference "morning".
    - time_preference: one of morning, afternoon, evening, or any short phrase the user used.

    Return ONLY a JSON object, no markdown fences, no comments.

    Input: "{user_input}" """

    log_event("parsing_tool", "llm_call_start", {"user_input": user_input})

    model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b").strip() or "llama3.2:3b"
    response = ollama.chat(
        model=model,
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

    content = response["message"]["content"]
    log_event("parsing_tool", "llm_raw_output", {"content": content})

    parsed = extract_json(content)
    parsed = _apply_explicit_iso_date_from_user(user_input, parsed)
    parsed = _drop_hallucinated_past_date(user_input, parsed)
    return merge_dateparser_date(user_input, parsed)