import os
from dotenv import load_dotenv
from chatbot.db import create_session, save_message, get_messages, delete_session
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

# Initialize LLM (GROK API via OpenAI wrapper if supported)
llm = ChatGroq(model="Gemma2-9b-It", api_key=GROK_API_KEY)

def chatbot(name: str, phone: str):
    # Normalize name (Abhishek = abhishek)
    name = name.strip().lower()

    session_id = f"{name}_{phone}"
    print(f"Session started for {name} ({phone})")

    # Load history
    history = get_messages(session_id)
    if history:
        print("Previous conversation found:")
        for h in history:
            print(f"{h['role']}: {h['content']}")
    else:
        create_session(session_id, name, phone)
        print("New session created.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "logout", "quit"]:
            delete_session(session_id)
            print("Session deleted. Logged out.")
            break

        # Save user message
        save_message(session_id, "human", user_input)

        # Get response from LLM
        response = llm.invoke(user_input)
        answer = response.content

        print("Bot:", answer)

        # Save bot response
        save_message(session_id, "ai", answer)


if __name__ == "__main__":
    name = input("Enter your first name: ")
    phone = input("Enter your phone: ")
    chatbot(name, phone)
