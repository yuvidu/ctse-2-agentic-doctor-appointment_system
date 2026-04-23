from crewai import Agent, LLM

ollama_llm = LLM(
    provider="ollama",
    model="llama3.2:3b",
    base_url="http://localhost:11434",
)

intent_agent_ai = Agent(
    role="Intent Analyzer",
    goal="Extract structured medical appointment intent",
    backstory="Expert in understanding user medical requests",
    verbose=True,
    llm=ollama_llm
)

availability_agent_ai = Agent(
    role="Availability Finder",
    goal="Find available doctors and slots",
    backstory="Knows doctor schedules",
    verbose=True,
    llm=ollama_llm
)

booking_agent_ai = Agent(
    role="Booking Manager",
    goal="Book appointment safely",
    backstory="Handles scheduling and conflicts",
    verbose=True,
    llm=ollama_llm
)

notification_agent_ai = Agent(
    role="Notification Manager",
    goal="Send appointment notifications",
    backstory="Handles sending notifications",
    verbose=True,
    llm=ollama_llm
)