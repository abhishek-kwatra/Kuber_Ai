import streamlit as st
import os
from dotenv import load_dotenv
from chatbot.supabase_history import SupabaseChatHistory
from langchain_core.messages import HumanMessage, AIMessage
from chatbot.llm_handler import (
    normalize_name,
    is_gold_related,
    is_greeting,
    generate_greeting_reply,
    generate_gold_reply,
    generate_investing_reply,
    is_investing_related,
    MODEL,
    trimmer,
)

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(page_title="KuberAI Lite - Gold Assistant", page_icon="🪙")
st.title("🪙 KuberAI Lite — Gold Investment Assistant")

# Logout button
if "session_id" in st.session_state:
    if st.button("🚪 Logout", key="logout_button"):
        st.session_state.clear()
        st.rerun()

# Step 1: User detail collection
if "session_id" not in st.session_state:
    st.subheader("Welcome! Please enter your details (name + phone) ")
    name = st.text_input("First name (only first name)", value="")
    phone = st.text_input("Phone number (digits only)", value="")

    if st.button("Start Chat", key="start_chat_button"):
        if not name or not phone:
            st.error("Please enter both name and phone.")
        else:
            norm_name = normalize_name(name)
            digits = "".join([c for c in phone if c.isdigit()])
            if not digits:
                st.error("Phone must contain digits.")
            else:
                session_id = f"{norm_name}_{digits}"
                st.session_state["session_id"] = session_id
                st.session_state["username"] = norm_name.capitalize()
                st.session_state["phone"] = digits
                st.success(f"Welcome, {st.session_state['username']} — loading your chat...")
                st.rerun()

# Step 2: Chat interface
if "session_id" in st.session_state:
    sid = st.session_state["session_id"]
    history = SupabaseChatHistory(session_id=sid)

    st.markdown(f"### Chat for: **{st.session_state.get('username', 'User')}** (session: `{sid}`)")

    # Show past chat messages
    for msg in history.messages:
        if msg["role"] == "human":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # Input from user
    user_input = st.chat_input("Ask about gold or investments...")
    if user_input:
        history.add_message({"type": "human", "content": user_input})
        st.chat_message("user").write(user_input)

        # Rebuild context
        context_messages = [
            HumanMessage(content=msg["content"]) if msg["role"] == "human" else AIMessage(content=msg["content"])
            for msg in history.messages
        ]
        trimmed_context = trimmer.invoke(context_messages) if trimmer else context_messages

        # Intent detection
        if is_gold_related(user_input):
            reply, _ = generate_gold_reply(user_input, trimmed_context)
            action = "offer_purchase"
        elif is_greeting(user_input):
            reply, _ = generate_greeting_reply(user_input, trimmed_context)
            action = "none"
        elif is_investing_related(user_input):
            reply, _ = generate_investing_reply(user_input, trimmed_context)
            action = "investment_education"
        else:
            # If the prompt does not fall under the above category and is not recognized
            if MODEL:
                try:
                    resp = MODEL.invoke(trimmed_context + [HumanMessage(content=user_input)])
                    reply = resp.content.strip()
                except Exception:
                    reply = "Hey! Let's stick to finance! I'm here to help with all your money-related questions. 💼"
            else:
                reply = "LLM is offline. Let's stick to finance! 💼"
            action = "none"

        # Save and show assistant reply
        history.add_message({"type": "ai", "content": reply})
        st.chat_message("assistant").write(reply)

        # Show investment button if applicable
        if action in ["offer_purchase", "investment_education"]:
            st.page_link("pages/investment.py", label="💰 Invest Now", icon="💼")
