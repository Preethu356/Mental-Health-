
import streamlit as st
import time
import io
from datetime import datetime

st.set_page_config(page_title="Mental Health Education Toolkit", layout="wide")

# --- Helpers / session state initialization ---
if "thought_records" not in st.session_state:
    st.session_state.thought_records = []
if "activities" not in st.session_state:
    st.session_state.activities = []
if "safety_plan" not in st.session_state:
    st.session_state.safety_plan = {"warning_signs": "", "coping": "", "contacts": ""}

def add_thought_record(record):
    st.session_state.thought_records.append(record)

def add_activity(act):
    st.session_state.activities.append({"activity": act, "done": False, "timestamp": datetime.utcnow().isoformat()})

def build_safety_text():
    sp = st.session_state.safety_plan
    txt = f"Safety Plan\n\nWarning signs:\n{sp['warning_signs']}\n\nCoping strategies:\n{sp['coping']}\n\nContacts & supports:\n{sp['contacts']}\n"
    return txt

# --- Layout ---
st.title("Mental Health Education Toolkit")
st.write("Practical techniques for learning and practicing mental health skills.")

with st.sidebar:
    st.header("Tools")
    section = st.radio("Choose a section", [
        "Psychoeducation",
        "Cognitive Techniques (CBT)",
        "Mindfulness & Relaxation",
        "Behavioral Activation",
        "Safety Plan",
        "Quick Quiz",
        "Resources"
    ])

# --- Psychoeducation ---
if section == "Psychoeducation":
    st.header("Psychoeducation")
    st.subheader("What is mental health literacy?")
    st.write("- Understanding common mental health problems and treatments.\n- Recognizing signs and when to seek help.\n- Learning skills to manage stress and emotions.")
    st.subheader("Core concepts")
    st.info("Thoughts → Emotions → Behaviors: changing one can change the others.")
    st.success("Small, consistent practices (5–15 minutes/day) build resilience.")
    st.subheader("Suggested micro-practices")
    st.write("- 3-item gratitude note each evening\n- 5-minute mindful breathing\n- Short behavioral experiments (try one small activity)")

# --- Cognitive Techniques (CBT) ---
elif section == "Cognitive Techniques (CBT)":
    st.header("CBT: Thought Record")
    st.write("Use this form to test unhelpful thoughts and generate balanced alternatives.")
    with st.form("thought_form", clear_on_submit=True):
        situation = st.text_input("Situation (what happened?)")
        automatic_thought = st.text_input("Automatic thought")
        emotion = st.selectbox("Primary emotion", ["Anxiety", "Sadness", "Anger", "Guilt", "Shame", "Other"])
        intensity = st.slider("Intensity (0-100)", 0, 100, 50)
        evidence_for = st.text_area("Evidence that supports the thought")
        evidence_against = st.text_area("Evidence that does NOT support the thought")
        balanced = st.text_area("More balanced thought / alternative explanation")
        submitted = st.form_submit_button("Save thought record")
        if submitted:
            rec = {
                "situation": situation,
                "thought": automatic_thought,
                "emotion": emotion,
                "intensity": int(intensity),
                "evidence_for": evidence_for,
                "evidence_against": evidence_against,
                "balanced": balanced,
                "time": datetime.utcnow().isoformat()
            }
            add_thought_record(rec)
            st.success("Thought record saved.")

    if st.session_state.thought_records:
        st.subheader("Recent thought records")
        for r in reversed(st.session_state.thought_records[-5:]):
            with st.expander(f"{r['emotion']} — {r['thought']} ({r['intensity']}%)"):
                st.write("Situation:", r["situation"])
                st.write("Evidence for:", r["evidence_for"] or "—")
                st.write("Evidence against:", r["evidence_against"] or "—")
                st.write("Balanced thought:", r["balanced"] or "—")
                st.write("Saved:", r["time"])

# --- Mindfulness & Relaxation ---
elif section == "Mindfulness & Relaxation":
    st.header("Mindfulness & Relaxation")
    st.write("Short guided exercises. Use headphones if helpful.")
    st.subheader("Box Breathing (4-4-4)")
    if st.button("Start 4-4-4 breathing"):
        placeholder = st.empty()
        rounds = 4
        try:
            for r in range(rounds):
                placeholder.markdown(f"Round {r+1}/{rounds} — Inhale for 4s")
                for i in range(4, 0, -1):
                    placeholder.markdown(f"⏱ Inhale: {i}")
                    time.sleep(1)
                placeholder.markdown("Hold for 4s")
                for i in range(4, 0, -1):
                    placeholder.markdown(f"⏱ Hold: {i}")
                    time.sleep(1)
                placeholder.markdown("Exhale for 4s")
                for i in range(4, 0, -1):
                    placeholder.markdown(f"⏱ Exhale: {i}")
                    time.sleep(1)
            placeholder.markdown("Done. Notice how your body feels.")
        except st.script_runner.RerunException:
            pass

    st.subheader("2-minute grounding exercise")
    st.write("Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste.")
    if st.checkbox("Start grounding timer (2 minutes)"):
        t_placeholder = st.empty()
        total = 120
        for s in range(total, -1, -1):
            mins = s // 60
            secs = s % 60
            t_placeholder.text(f"Time remaining: {mins:02d}:{secs:02d}")
            time.sleep(1)
        t_placeholder.text("Finished. Take a slow breath.")

# --- Behavioral Activation ---
elif section == "Behavioral Activation":
    st.header("Behavioral Activation")
    st.write("Schedule small, rewarding activities to boost mood.")
    with st.form("activity_form", clear_on_submit=True):
        act = st.text_input("Add an activity (e.g., short walk, call a friend)")
        importance = st.selectbox("Importance", ["Low", "Medium", "High"])
        add = st.form_submit_button("Add activity")
        if add and act.strip():
            add_activity({"activity": act.strip(), "importance": importance, "done": False, "time": datetime.utcnow().isoformat()})
            st.success("Activity added.")

    if st.session_state.activities:
        st.subheader("Planned activities")
        for i, a in enumerate(st.session_state.activities):
            cols = st.columns([1, 6, 2])
            done = cols[0].checkbox("", value=a.get("done", False), key=f"act_{i}")
            if done and not a.get("done"):
                st.session_state.activities[i]["done"] = True
                st.session_state.activities[i]["completed_time"] = datetime.utcnow().isoformat()
            cols[1].write(f"**{a['activity']}** — {a.get('importance','')}")
            if a.get("done"):
                cols[2].write("✅ Done")
            else:
                if cols[2].button("Mark done", key=f"mark_{i}"):
                    st.session_state.activities[i]["done"] = True
                    st.session_state.activities[i]["completed_time"] = datetime.utcnow().isoformat()
                    st.experimental_rerun()
    else:
        st.info("No activities yet. Add one above.")

# --- Safety Plan ---
elif section == "Safety Plan":
    st.header("Safety Plan (personalized)")
    st.write("Create a brief safety plan. If you are in immediate danger, call local emergency services.")
    with st.form("safety_form"):
        st.session_state.safety_plan["warning_signs"] = st.text_area("Warning signs (thoughts/changes you notice)", value=st.session_state.safety_plan["warning_signs"])
        st.session_state.safety_plan["coping"] = st.text_area("Coping strategies you can try on your own", value=st.session_state.safety_plan["coping"])
        st.session_state.safety_plan["contacts"] = st.text_area("Supportive contacts (friends, family, professionals)", value=st.session_state.safety_plan["contacts"])
        save_sp = st.form_submit_button("Save safety plan")
        if save_sp:
            st.success("Safety plan saved.")

    st.download_button("Download safety plan (TXT)", build_safety_text().encode("utf-8"), file_name="safety_plan.txt", mime="text/plain")
    st.warning("If you feel at immediate risk, contact emergency services or a crisis hotline in your area.")

# --- Quick Quiz ---
elif section == "Quick Quiz":
    st.header("Quick quiz — check understanding")
    st.write("Choose the best answer.")
    questions = [
        {
            "q": "Which of these is a CBT technique?",
            "options": ["Exposure to feared situations", "Journaling thoughts and evidence", "Physical exercise only", "Ignoring thoughts"],
            "answer": 1
        },
        {
            "q": "A good mindfulness practice is:",
            "options": ["Multitasking while breathing", "Judging thoughts as bad", "Observing sensations without reacting", "Forcing emotions away"],
            "answer": 2
        },
        {
            "q": "Behavioral activation focuses on:",
            "options": ["Avoiding activities to prevent stress", "Scheduling reinforcing activities to improve mood", "Only talking about feelings", "Immediate resolution of all problems"],
            "answer": 1
        }
    ]
    score = 0
    user_answers = []
    for idx, item in enumerate(questions):
        st.write(f"Q{idx+1}. {item['q']}")
        choice = st.radio("", item["options"], key=f"q{idx}")
        user_answers.append(item["options"].index(choice))
    if st.button("Submit quiz"):
        for i, ua in enumerate(user_answers):
            if ua == questions[i]["answer"]:
                score += 1
        st.info(f"You scored {score}/{len(questions)}")
        st.write("Correct answers:")
        for i, item in enumerate(questions):
            st.write(f"Q{i+1}: {item['options'][item['answer']]}")

# --- Resources ---
elif section == "Resources":
    st.header("Resources & next steps")
    st.write("- If you need professional help, contact a licensed mental health provider.")
    st.write("- Crisis lines vary by country. If you are in immediate danger call emergency services.")
    st.subheader("Educational resources")
    st.markdown("- [Mindfulness exercises - NHS UK](https://www.nhs.uk/mental-health/feelings-symptoms-behaviours/feelings/mindfulness/)")
    st.markdown("- [CBT guides - Beck Institute](https://beckinstitute.org/)")
    st.markdown("- [Psychoeducation overview - WHO](https://www.who.int/mental_health)")

    st.subheader("Printable worksheet")
    worksheet = (
        "Mental Health Toolkit Worksheet\n\n"
        "1) Today I noticed:\n\n"
        "2) Thought I challenged:\n\n"
        "3) Activity I scheduled:\n\n"
        "4) Coping strategies to try:\n\n"
        "5) Support contacts:\n\n"
    )
    st.download_button("Download worksheet (TXT)", worksheet.encode("utf-8"), file_name="mh_worksheet.txt", mime="text/plain")

# Footer
st.markdown("---")
st.caption("This app provides educational tools and is not a substitute for professional care.")
# ...existing code...
