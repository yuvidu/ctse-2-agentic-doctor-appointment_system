from agents.intent_agent import intent_agent

if __name__ == "__main__":
    while True:
        user_input = input("\nEnter request: ")

        result = intent_agent(user_input)

        print("\nFinal Output:")
        print(result)