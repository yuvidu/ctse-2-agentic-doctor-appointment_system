from unittest import result
from agents.intent_agent import intent_agent

from agents.crew_ai.crewai_agents import (
    intent_agent_ai,
    availability_agent_ai,
    booking_agent_ai,
    notification_agent_ai
)
from agents.notification_agent import notification_agent
import uuid

from crewai import Task, Crew


# from agents.availability_agent import availability_agent
# from agents.booking_agent import booking_agent
# from agents.notification_agent import notification_agent



# if __name__ == "__main__":
#     while True:
#         user_input = input("\nEnter request: ")

#         result = intent_agent(user_input)

#         print("\nFinal Output:")
#         print(result)


def run_system(user_input: str) -> dict:
    #global state for agents to share
    state = {
        "user_input": user_input,
        "intent": {},
        "doctor": "",
        "available_slots": [],
        "appointment": {},
        "status": "",
        "errors": []
    }
    # step 1 intent agent and extract intent

    intent_task = Task(
        description=f"Extract intent from: {user_input}",
        agent=intent_agent_ai,
        expected_output="Structured JSON"
    )

    availability_task = Task(
        description=f"Find doctors and available slots for intent: {user_input}",
        agent=availability_agent_ai,
        expected_output="Doctor list and available slots"
    )

    booking_task = Task(
        description=f"Reserve best available slot for the parsed intent: {user_input}",
        agent=booking_agent_ai,
        expected_output="Booking confirmation"
    )

    notification_task = Task(
        description=f"Send notification to user about booking: {user_input}",
        agent=notification_agent_ai,
        expected_output="Notification status"
    )

    crew = Crew(
        agents=[intent_agent_ai, availability_agent_ai, booking_agent_ai, notification_agent_ai],
        tasks=[intent_task, availability_task, booking_task, notification_task],
        verbose=True
    )

    # crew = Crew(
    #     agents=[intent_agent_ai, availability_agent_ai, booking_agent_ai],
    #     tasks=[intent_task, availability_task, booking_task],
    #     verbose=True,
    #     llm=ollama_llm
    #     process=ollama_llm
    # )

    crew.kickoff()


    intent_response = intent_agent(state)
    state["intent"] = intent_response
    state["status"] = intent_response.get("status", "")
    state["errors"] = intent_response.get("errors", [])

    # Stop if incomplete or error
    if intent_response.get("status") != "complete":
        return state

    # Step 2/3: Lightweight availability and booking simulation (temporary)
    parsed = intent_response.get("intent", {}) if isinstance(intent_response, dict) else {}
    date = parsed.get("date", "")
    time_pref = parsed.get("time_preference", "").lower() if isinstance(parsed.get("time_preference", ""), str) else ""

    if "afternoon" in time_pref:
        hour = "14:00:00"
    elif "evening" in time_pref:
        hour = "18:00:00"
    else:
        hour = "09:00:00"

    if date:
        time_iso = f"{date}T{hour}"
    else:
        time_iso = f"2026-05-03T{hour}"

    appointment = {
        "appointment_id": f"APT{uuid.uuid4().hex[:8]}",
        "user_name": "Unknown",
        "user_contact": "",
        "doctor": "Assigned Doctor",
        "specialization": parsed.get("specialization", ""),
        "time_iso": time_iso,
        "channel": "sms",
    }

    state["appointment"] = appointment

    # Step 4: Notification agent - send confirmation
    state = notification_agent(state)



    return state 

if __name__ == "__main__":    
    while True:
        user_input = input("\nEnter request: ")
        result = run_system(user_input)
        print("\nFinal Output:")
        print(result)

    
    