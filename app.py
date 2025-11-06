import streamlit as st
import pandas as pd
import datetime
from helpers import get_suggestions, calming_breathing_text

st.set_page_config(page_title="Mental Health Assistant", page_icon="🧠", layout="centered")

st.title("🧠 Mental Health Assistant — Streamlit")
st.write("This non-clinical assistant offers self-help tools, mood tracking, and resources. Not a substitute for professional help.")

# --- Sidebar: user info and mood logging ---
st.sidebar.header("Mood Tracker")
name = st.sidebar.text_input("Your name (optional)")
mood = st.sidebar.selectbox("How are you feeling right now?", ["Very good","Good","Okay","Down","Very down"])
notes = st.sidebar.text_area("Short notes (what's on your mind?)", "", max_chars=500)
save = st.sidebar.button("Log mood")

if "mood_logs" not in st.session_state:
    st.session_state["mood_logs"] = []

if save:
    entry = {"timestamp": datetime.datetime.now().isoformat(), "name": name, "mood": mood, "notes": notes}
    st.session_state["mood_logs"].append(entry)
    st.sidebar.success("Mood saved ✅")

if st.sidebar.button("Download mood logs (CSV)"):
    if st.session_state["mood_logs"]:
        df = pd.DataFrame(st.session_state["mood_logs"])
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("Download CSV", data=csv, file_name="mood_logs.csv", mime="text/csv")
    else:
        st.sidebar.info("No mood logs yet.")

# --- Main: Chat-like suggestions ---
st.header("Quick check-in")
user_input = st.text_area("Talk to the assistant (type how you're feeling / what's happening):", "", max_chars=1000, height=120)
if st.button("Get supportive suggestions"):
    if not user_input.strip():
        st.warning("Please enter something you'd like support with.")
    else:
        suggestions = get_suggestions(user_input)
        st.subheader("Suggestions & self-help actions")
        for i, s in enumerate(suggestions, 1):
            st.markdown(f"**{i}.** {s}")

# --- Breathing exercise ---
st.header("Calming breathing exercise")
if st.button("Start breathing exercise (1 min)"):
    st.info("Follow the prompts below. Click the buttons as you breathe.")
    st.markdown(calming_breathing_text())

# --- Resources & Crisis Notice ---
st.header("Resources & Safety")
st.markdown(
    "Important: This assistant is not a replacement for professional help. "
    "If you are in immediate danger or having a medical/mental-health emergency, "
    "please contact local emergency services right away."
)
st.markdown(
    "Crisis resources (examples):\n"
    "- In India: National Helpline - 9152987821 (or contact local emergency services)\n"
    "- International: Find local hotlines at organizations such as befrienders.org or your country's health department."
)

st.subheader("Further reading")
st.write("- Grounding: 5-4-3-2-1 sensory technique")
st.write("- Sleep hygiene, routine, and small daily activities can help mood.")
st.write("- If symptoms persist or worsen, seek a licensed mental health professional.")

# --- Show mood logs table in main area ---
if st.session_state["mood_logs"]:
    st.markdown("---")
    st.subheader("Your recent mood logs (session only)")
    df = pd.DataFrame(st.session_state["mood_logs"])
    df_display = df.copy()
    df_display["timestamp"] = pd.to_datetime(df_display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(df_display.sort_values("timestamp", ascending=False))
