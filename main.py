from agent import handle_query

def chat_session():
    print("\n---")
    print("INFO: Financial Agent Initialized.")
    print("You can now ask questions about stock prices or general topics.")
    print("Type 'exit', 'quit', or 'q' to end the session.")
    print("---")

    while True:
        try:
            query = input("You: ")
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D
            print("\n🤖 Agent: Goodbye!")
            break

        if query.lower() in ['exit', 'quit', 'q']:
            print("🤖 Agent: Goodbye!")
            break

        if not query.strip(): # Re-prompt if user 'ENTERS' by mistake
            continue

        print("\nINFO: Agent is thinking...")
        final_answer = handle_query(query)

        print("\n--- Agent's Response ---")
        print(final_answer.strip())
        print("------------------------\n")

if __name__ == "__main__":
    chat_session()