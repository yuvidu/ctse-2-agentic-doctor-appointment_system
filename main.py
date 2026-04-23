from unittest import result
from agents.intent_agent import intent_agent

from agents.crew_ai.crewai_agents import (
    intent_agent_ai,
    availability_agent_ai,
    booking_agent_ai,
    notification_agent_ai
)

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

    crew = Crew(
        agents=[intent_agent_ai],
        tasks=[intent_task],
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

    #Stop if incomplete or error
    if intent_response.get("status") != "complete":
        return state

    # Step 2 (later)
    # state.update(availability_agent(state))

    # Step 3 (later)
    # state.update(booking_agent(state))

    # Step 4 (later)
    # state.update(notification_agent(state))



    return state 

if __name__ == "__main__":    
    while True:
        user_input = input("\nEnter request: ")
        result = run_system(user_input)
        print("\nFinal Output:")
        print(result)

    
    