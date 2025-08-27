# chatbot/llm_handler.py
import os
import re
import random
from typing import Tuple
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from dotenv import load_dotenv

load_dotenv()


GREETINGS = ["hi", "hello", "hey", "good morning", "good evening"]

# simple keyword approach + fallback LLM generation for gold replies
GOLD_KEYWORDS = ["gold", "digital gold", "invest in gold", "buy gold", "gold price", ]

INVESTING_KEYWORDS = ["invest", "investment", "returns", "financial planning", "investing", "finance", "mutual fund", "sip", "stocks", "returns", "wealth"]


# Facts used for deterministic grounding (reduces hallucination)
GOLD_FACTS = [
    "Gold is commonly viewed as a hedge against inflation and currency volatility.",
    "Digital gold allows fractional investments—some platforms let you start with ₹100.",
    "Adding a small allocation to gold can improve portfolio diversification.",
    "Gold can be volatile short-term; consider medium-to-long-term horizon for preservation."
]

GROK_API_KEY = os.getenv("GROK_API_KEY")


# Initialize model
if not GROK_API_KEY:
    # We allow offline development; you can still use the facts fallback
    MODEL = None
else:
    MODEL = ChatGroq(model="Gemma2-9b-It", api_key=GROK_API_KEY)
    if MODEL: 
        trimmer = trim_messages(
        max_tokens=200,       # you asked for 20 tokens
        strategy="last",
        token_counter=MODEL, # 👈 uses your ChatGroq model
        include_system=True,
        allow_partial=False,
        start_on="human"
        )
    else:
        trimmer = None

def trim_context(messages):
    # Trims a chat history so it doesn't exceed the token limit.
    if trimmer:
        return trimmer.invoke(messages)
    return messages   # fallback: if MODEL=None, just return full messages


def normalize_name(name: str) -> str:
    """Normalize name: keep first token, lowercase"""
    return name.strip().split()[0].lower()


def is_gold_related(user_input: str) -> bool:
    txt = user_input.lower()
    return any(k in txt for k in GOLD_KEYWORDS)

def is_greeting(user_input: str)-> bool:
    txt= user_input.lower()
    return any(k in txt for k in GREETINGS)


def is_investing_related(user_input: str) -> bool:
    txt = user_input.lower()
    return any(word in txt for word in INVESTING_KEYWORDS)



def generate_greeting_reply(user_input: str, context_messages=None) -> Tuple[str, list]:
    """Generate reply when user greets. Uses context + system role."""
    if MODEL:
        try:
            messages = []
            if context_messages:
                messages.extend(context_messages)

            # Define assistant role
            messages.insert(0, SystemMessage(content=(
                "You are a warm, friendly assistant. "
                "When greeted, reply in 1–2 short sentences, "
                "then gently mention digital gold investing with 2–3 benefits. "
                "Keep it conversational."
            )))
            # Adding user latest message
            messages.append(HumanMessage(content=user_input))
            resp = MODEL.invoke(messages)
            return resp.content.strip(), []
        except Exception as e:
            print("LLM error in greeting:", e)

    return random.choice(GREETINGS), []


def generate_gold_reply(user_input: str, context_messages=None) -> Tuple[str, list]:
    """Generate reply when user asks about gold. Always use facts."""
    facts = random.sample(GOLD_FACTS, k=min(2, len(GOLD_FACTS)))

    if MODEL:
        try:
            messages = []
            if context_messages:
                messages.extend(context_messages)
            # Define assistant role
            messages.insert(0, SystemMessage(content=(
                "You are a concise financial assistant for Indian users. "
                "Use factual information about gold investing, "
                "include 1–2 key benefits, "
                "and politely end with: 'Would you like to purchase digital gold today?'"
            )))
            # Adding user latest message
            messages.append(HumanMessage(content=user_input))
            resp = MODEL.invoke(messages)
            return resp.content.strip(), facts
        except Exception as e:
            print("LLM error in gold reply:", e)

    return f"{facts[0]} Would you like to purchase digital gold today?", facts


def generate_investing_reply(user_input: str, context_messages=None) -> Tuple[str, list]:
    """Generate reply when user asks about investing in general."""
    if MODEL:
        try:
            messages = []
            if context_messages:
                messages.extend(context_messages)
            
            # Define assistant role
            messages.insert(0, SystemMessage(content=(
                "You are a friendly financial assistant for Indian users. "
                "Explain investing in very simple words, 3–5 sentences, "
                "using examples like SIPs, stocks, or digital gold. "
                "Avoid jargon. Be warm and approachable."
            )))
            
            # Adding user latest message
            messages.append(HumanMessage(content=user_input))
            resp = MODEL.invoke(messages)
            return resp.content.strip(), []
        except Exception as e:
            print("LLM error in investing reply:", e)

    return "Investing means putting your money into assets like mutual funds, gold, or stocks to grow it over time.", []
