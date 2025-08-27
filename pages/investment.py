import streamlit as st
import requests
from datetime import datetime
from chatbot.supabase_history import SupabaseChatHistory
import os

sid = st.session_state["session_id"]
investment = SupabaseChatHistory(session_id=sid)

# Function: Get Live Gold Price

def get_live_price_inr_per_gram():
    try:
        url = "https://api.gold-api.com/price/XAU"
        response = requests.get(url, timeout=5)
        data = response.json()

        usd_per_ounce = data.get("price", 0)
        if not usd_per_ounce:
            return None

        usd_per_gram = usd_per_ounce / 31.1035
        usd_to_inr = 83.0  # approx conversion 
        inr_per_gram = usd_per_gram * usd_to_inr

        return round(inr_per_gram, 2)

    except Exception as e:
        st.error(f"Error fetching gold price: {e}")
        return None

# Investment Page
st.set_page_config(page_title="Gold Investment", page_icon="💰")
st.title("💰 Gold Investment Page")

# Check session
if "session_id" not in st.session_state:
    st.warning("Please login first from the main page.")
    st.stop()

sid = st.session_state["session_id"]

# Get live price
gold_price = get_live_price_inr_per_gram()
if gold_price:
    st.info(f"📈 Current Digital Gold Rate: **₹{gold_price} per gram**")
else:
    st.warning("Could not fetch current gold rate right now.")
    st.stop()

# User input: Amount
amount = st.number_input("Enter amount to invest (₹)", min_value=10, step=100)

# Dynamic calculation
grams = 0
if amount > 0 and gold_price:
    grams = round(amount / gold_price, 4)
    st.success(f" You will receive **{grams} grams** of digital gold.")

# Confirm investment
if st.button("✅ Confirm Investment"):
    if amount <= 0:
        st.error("Please enter a valid amount.")
    else:
        try:
            investment.add_investment(
                name=st.session_state.get("username"),
                phone=st.session_state.get("phone")
            )
            st.success(f"Investment recorded: ₹{amount} → {grams} g at ₹{gold_price}/g")
        except Exception as e:
            st.error(f"Error saving investment: {e}")
