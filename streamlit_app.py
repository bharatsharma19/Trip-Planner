# streamlit_app.py
import streamlit as st
import requests
import uuid

# ------------------------#
# CONFIGURATION
# ------------------------#
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="🌍 The Ultimate Trip Planner",
    page_icon="✈️",
    layout="wide",
)

# ------------------------#
# SESSION STATE
# ------------------------#
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trip_plan" not in st.session_state:
    st.session_state.trip_plan = {}


# ------------------------#
# HELPER FUNCTIONS
# ------------------------#
def display_trip_plan(plan):
    """Renders the structured trip plan in a clean and robust way."""
    if not plan or (plan.get("status") == "planning" and not plan.get("destination")):
        return

    st.markdown("---")
    st.subheader("✨ Your Trip Plan ✨")

    # Display high-level route for multi-city trips
    if route := plan.get("route"):
        route_str = " -> ".join(
            [
                f"{stop.get('city', '')} ({stop.get('num_days', '')} days)"
                for stop in route
            ]
        )
        st.markdown(f"**Your Route:** {route_str}")

    # Display top-level summary
    if dest := plan.get("destination"):
        st.write(f"**Destination:** {dest}")
    if dur := plan.get("duration_days"):
        st.write(f"**Duration:** {dur} days")
    if interests := plan.get("interests"):
        st.write(f"**Interests:** {', '.join(interests)}")

    # Display real-time flight options
    if flights := plan.get("flights"):
        st.markdown("#### ✈️ Flight Options")
        for flight in flights:
            with st.container(border=True):
                st.write(f"**{flight.get('airline', 'N/A')}**")
                col1, col2, col3 = st.columns(3)
                col1.metric("Price", str(flight.get("price", "N/A")))
                col2.metric("Stops", str(flight.get("stops", "N/A")))
                col3.metric("Departure", flight.get("departure_time", "N/A"))

    # Display real-time hotel options
    if accommodation := plan.get("accommodation"):
        st.markdown("#### 🏨 Hotel Options")
        for hotel in accommodation:
            with st.container(border=True):
                st.write(f"**{hotel.get('name', 'N/A')}**")
                col1, col2, col3 = st.columns(3)
                price_str = str(hotel.get("price_per_night", "N/A"))
                col1.metric("Price/Night", price_str)
                col2.metric("Rating", f"{hotel.get('rating', 'N/A')} ⭐")
                col3.metric("Reviews", f"{hotel.get('review_score', 'N/A')}/10")

    # Display the detailed daily itinerary
    if itinerary := plan.get("itinerary"):
        st.markdown("#### 🗓️ Itinerary")
        for day in itinerary:
            with st.expander(f"**Day {day.get('day')}: {day.get('title', '')}**"):
                if activities := day.get("activities"):
                    st.markdown("##### Activities")
                    for activity in activities:
                        st.markdown(f"- {activity}")
                if meals := day.get("meals"):
                    st.markdown("##### Meal Suggestions")
                    if isinstance(meals, dict):
                        for meal_type, place in meals.items():
                            st.markdown(f"- **{meal_type.capitalize()}:** {place}")
                    else:
                        st.markdown(f"- {meals}")

    # Display the final budget
    if budget := plan.get("budget"):
        st.markdown("#### 💰 Budget Breakdown")
        st.table(budget)


# ------------------------#
# HEADER
# ------------------------#
st.title("✈️ The Ultimate Trip Planner")
st.markdown(
    "Your AI-powered travel agent for creating perfect, personalized itineraries from start to finish."
)

# ------------------------#
# CHAT INTERFACE
# ------------------------#
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

display_trip_plan(st.session_state.trip_plan)

if prompt := st.chat_input(
    "Where to next? (e.g., 'Plan a 7-day trip to Goa from Delhi')"
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(
            "🧠 Planning your ultimate adventure... This may take a moment as I search for live data..."
        ):
            try:
                payload = {"query": prompt, "session_id": st.session_state.session_id}
                response = requests.post(
                    f"{API_BASE_URL}/query", json=payload, timeout=300
                )
                response.raise_for_status()

                data = response.json()
                bot_response = data.get(
                    "answer", "I'm not sure how to respond to that."
                )
                st.session_state.trip_plan = data.get("plan", {})

                st.markdown(bot_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": bot_response}
                )
                st.rerun()

            except requests.RequestException as e:
                error_detail = e.response.json().get("detail") if e.response else str(e)
                st.error(f"API Error: {error_detail}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
