import streamlit as st
import requests

# ------------------------#
# 🔧 CONFIGURATION
# ------------------------#
BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="🌍 Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------#
# 🎯 HEADER
# ------------------------#
st.markdown(
    """
    <style>
        .user-bubble {
            background-color: #e6f0ff;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .bot-bubble {
            background-color: #f1f8e9;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .message-container {
            margin-top: 20px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("✈️ Trip Planner")
st.subheader("Plan your dream trip effortlessly 🌍")
st.write(
    "Tell me where you're headed and what you're into — I'll handle the itinerary."
)

# ------------------------#
# 🔄 SESSION STATE INIT
# ------------------------#
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------#
# 📝 USER INPUT FORM
# ------------------------#
with st.form("trip_form", clear_on_submit=True):
    user_query = st.text_area(
        "🗺️ Describe your trip (e.g. destination, interests, travel dates):",
        placeholder="I'm going to Japan for 10 days and love food, temples, and anime...",
        height=120,
    )
    submitted = st.form_submit_button("🚀 Plan My Trip")

if submitted and user_query.strip():
    st.session_state.messages.append({"role": "user", "content": user_query.strip()})

    with st.spinner("🧠 Crafting the perfect plan..."):
        try:
            response = requests.post(
                f"{BASE_URL}/query", json={"query": user_query.strip()}, timeout=60
            )
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer received.")
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                error_msg = response.json().get("error", "Something went wrong.")
                st.error(f"❌ API Error: {error_msg}")
        except requests.RequestException as e:
            st.error(f"⚠️ Request failed: {e}")

# ------------------------#
# 💬 CONVERSATION HISTORY
# ------------------------#
if st.session_state.messages:
    st.markdown("### 💬 Conversation History")
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-bubble'><strong>🧑 You:</strong><br>{msg['content']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='bot-bubble'><strong>🤖 Trip Planner:</strong><br>{msg['content']}</div>",
                unsafe_allow_html=True,
            )

# ------------------------#
# 📌 FOOTER / TIPS
# ------------------------#
st.markdown("---")
st.markdown(
    "✅ _Tip: The more details you give (weather prefs, budget, activities), the better the plan!_"
)
