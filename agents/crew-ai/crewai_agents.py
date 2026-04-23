from crewai import Agent

intent_agent_ai = Agent(
    role="Intent Analyzer",
    goal="Extract structured medical appointment intent",
    backstory="Expert in understanding user medical requests",
    verbose=True
)

availability_agent_ai = Agent(
    role="Availability Finder",
    goal="Find available doctors and slots",
    backstory="Knows doctor schedules",
    verbose=True
)

booking_agent_ai = Agent(
    role="Booking Manager",
    goal="Book appointment safely",
    backstory="Handles scheduling and conflicts",
    verbose=True
)
notification_agent_ai = Agent(
    role="Notification Manager",
    goal="Send appointment notifications",
    backstory="Handles sending notifications",
    verbose=True
)