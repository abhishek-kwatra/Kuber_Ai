import streamlit as st
import requests
from datetime import datetime
from chatbot.supabase_history import SupabaseChatHistory
from zoneinfo import ZoneInfo
import os


# Investment Page Config
st.set_page_config(page_title="Gold Investment", page_icon="💰")
st.title("💰 Gold Investment Page")

# Check session
if "session_id" not in st.session_state:
    st.warning("Please login first from the main page.")
    st.stop()

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
        usd_to_inr = 83.0  # approximate conversion
        inr_per_gram = usd_per_gram * usd_to_inr

        return round(inr_per_gram, 2)

    except Exception as e:
        st.error(f"Error fetching gold price: {e}")
        return None

# Fetch current gold price
gold_price = get_live_price_inr_per_gram()
if gold_price:
    st.info(f"📈 Current Digital Gold Rate: **₹{gold_price} per gram**")
else:
    st.warning("Could not fetch current gold rate right now.")
    st.stop()

# User input: Amount to invest
amount = st.number_input("Enter amount to invest (₹)", min_value=10, step=100)

# Dynamic grams calculation
grams = 0
if amount > 0 and gold_price:
    grams = round(amount / gold_price, 4)
    st.success(f"💰 You will receive **{grams} grams** of digital gold.")

# Confirm investment button
if st.button("✅ Confirm Investment"):
    if amount <= 0:
        st.error("Please enter a valid amount.")
    else:
        try:
            investment.add_investment(
                name=st.session_state.get("username"),
                phone=st.session_state.get("phone"),
                amount=amount,
            )
            st.success(f"Investment recorded: ₹{amount} → {grams} g at ₹{gold_price}/g")
        except Exception as e:
            st.error(f"Error saving investment: {e}")

# Show previous investments
previous_investments = investment.get_investments()
if previous_investments:
    st.markdown("### 💼 Your Previous Investments")
    for inv in previous_investments:
        utc_time = datetime.fromisoformat(inv['created_at'].replace("Z", "+00:00"))
        ist_time = utc_time.astimezone(ZoneInfo("Asia/Kolkata"))
        new_time = ist_time.strftime("%d/%m/%Y %H:%M")
        st.write(f"{inv['name']} invested -> ₹{inv['amount']} on {new_time}")
