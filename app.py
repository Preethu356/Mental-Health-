# app.py
"""
Streamlit Mental Health Assistant (refined)
Requires:
 - streamlit
 - openai (OpenAI Python SDK)
 - python-dotenv (optional, for local env loading)
 - toml (for config file)

Place a `config.toml` file next to this script or rely on defaults defined below.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional

import streamlit as st
import toml
from dotenv import load_dotenv

# Try to import the OpenAI client. If unavailable, let get_ai_response fail gracefully.
try:
    import openai
except Exception:
    openai = None  # handled later

# --- Basic logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mh_assistant")

# --- Load .env (local dev convenience) ---
load_dotenv()

# --- Config defaults ---
DEFAULT_CONFIG = {
    "app": {
        "title": "Mental Health Assistant",
        "warning_message": "This is not a substitute for professional care.",
        "crisis_hotline": "Local crisis hotline (replace in config)",
        "crisis_text": "Text HELP to 741741 (replace per country)"
    },
    "model": {
        "default_model": "gpt-4o-mini",  # change to your preferred model
        "max_tokens": 512,
        "temperature": 0.7
    },
    "style": {
        "background_color": "#FFFFFF"
    }
}

# --- Load configuration from TOML with safe fallback ---
def load_config(path: str = "config.toml") -> Dict[str, Any]:
    try:
        if os.path.exists(path):
            cfg = toml.load(path)
            # Merge defaults
            merged = DEFAULT_CONFIG.copy()
            for key in DEFAULT_CONFIG:
                if key in cfg:
                    merged[key].update(cfg.get(key, {}))
            return merged
        else:
            logger.warning("config.toml not found — using default configuration.")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.exception("Failed to load config.toml; using defaults.")
        return DEFAULT_CONFIG

config = load_config("config.toml")
app_config = config["app"]
model_config = config["model"]
style_config = config["style"]

# --- Streamlit page config & CSS ---
st.set_page_config(page_title=app_config.get("title", "Mental Health Assistant"), page_icon="🧠", layout="centered")

st.markdown(
    f"""
    <style>
        .main {{ background-color: {style_config.get("background_color", "#FFFFFF")}; }}
        .stChatMessage {{ padding: 0.75rem; }}
        .warning-box {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin: 0.75rem 0;
        }}
        .crisis-box {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 0.5rem;
            padding: 0.75rem;
            margin: 0.75rem 0;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session state initialization ---
def initialize_session_state():
    if "messages" not in st.session_state:
        system_prompt = (
            "You are a helpful, empathetic mental health information assistant.\n\n"
            "ROLE:\n"
            "- Provide general psychoeducation and supportive, validating responses.\n"
            "- Offer evidence-based coping strategies and brief self-help suggestions.\n\n"
            "CRITICAL SAFETY RULES:\n"
            "- You are NOT a licensed therapist or crisis counselor.\n"
            "- Do NOT provide diagnoses or long treatment plans.\n"
            "- If user mentions self-harm/suicide/imminent danger, acknowledge, provide crisis resources, "
            "encourage contacting emergency services, and keep the response brief and safety-focused.\n\n"
            f"Include this disclaimer in your first assistant message: \"{app_config.get('warning_message')}\""
        )

        # System message followed by a friendly assistant greeting
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": (
                f"Hello — I'm here to provide general mental health information and support. "
                f"{app_config.get('warning_message')} How can I help you today?"
            )}
        ]

# --- Crisis detection & response ---
CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end it all", "want to die",
    "harm myself", "self harm", "hurt myself", "not want to live",
    "i'm going to kill myself", "i want to die", "suicidal"
]

def contains_crisis_keywords(text: str) -> bool:
    text_lower = (text or "").lower()
    return any(k in text_lower for k in CRISIS_KEYWORDS)

def handle_crisis_response() -> str:
    # Keep this short and safety focused
    hotline = app_config.get("crisis_hotline", "Local crisis hotline")
    textline = app_config.get("crisis_text", "Crisis text line")
    return (
        "I hear that you're in a lot of pain, and I'm very concerned about your safety.\n\n"
        "**Please reach out for immediate help:**\n"
        f"- **Crisis Hotline:** {hotline}\n"
        f"- **Crisis Text Line:** {textline}\n"
        "- **Emergency Services:** Call your local emergency number now if you are in immediate danger.\n\n"
        "You don't have to go through this alone — please contact someone who can help right now."
    )

# --- OpenAI API call wrapper (safe) ---
def get_openai_client() -> Optional[Any]:
    """
    Returns an OpenAI client instance if openai is available and API key is set.
    Uses st.secrets['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'] if present, else environment variable.
    """
    if openai is None:
        return None

    api_key = None
    # Check streamlit secrets first (recommended), then env var
    if st.secrets.get("OPENAI_API_KEY"):
        api_key = st.secrets["OPENAI_API_KEY"]
    else:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    # Newer OpenAI Python SDK patterns might differ; using flexible initialization
    try:
        # If OpenAI SDK expects configuration via env var, ensure it's set (safe for client usage)
        os.environ["OPENAI_API_KEY"] = api_key
        client = openai.OpenAI(api_key=api_key) if hasattr(openai, "OpenAI") else openai
        return client
    except Exception as e:
        logger.exception("Failed to initialize OpenAI client: %s", e)
        return None

def trim_messages_for_tokens(messages: List[Dict[str, str]], max_exchanges: int = 6) -> List[Dict[str, str]]:
    """
    Keep the last `max_exchanges` entries but always keep the system message at index 0.
    """
    if not messages:
        return messages
    system = [m for m in messages if m.get("role") == "system"]
    others = [m for m in messages if m.get("role") != "system"]
    keep = others[-max_exchanges:]
    return system + keep

def get_ai_response(messages: List[Dict[str, str]]) -> str:
    """
    Calls OpenAI chat completion endpoint and returns assistant text.
    On any failure, returns a friendly error message.
    """
    client = get_openai_client()
    if client is None:
        logger.warning("OpenAI client not available or API key missing.")
        return "AI unavailable: no OpenAI API key configured. Provide one in the sidebar or set it as a secret."

    # Trim messages to conserve tokens
    messages_to_send = trim_messages_for_tokens(messages, max_exchanges=6)
    try:
        # Depending on SDK shape, there are multiple APIs; this matches the `client.chat.completions.create` pattern
        resp = client.chat.completions.create(
            model=model_config.get("default_model"),
            messages=messages_to_send,
            max_tokens=model_config.get("max_tokens", 512),
            temperature=model_config.get("temperature", 0.7),
        )

        # Extract text safely
        if hasattr(resp, "choices") and len(resp.choices) > 0:
            # Many SDKs use resp.choices[0].message.content
            choice = resp.choices[0]
            # Support different response structures safely
            if hasattr(choice, "message") and getattr(choice.message, "content", None):
                return choice.message.content
            elif getattr(choice, "text", None):
                return choice.text
        # Fallback text extraction
        return str(resp)
    except Exception as e:
        logger.exception("OpenAI request failed: %s", e)
        return "I'm having trouble responding right now. Please try again later."

# --- Main App ---
def main():
    initialize_session_state()

    # --- Sidebar: Safety, API key, controls ---
    with st.sidebar:
        st.title("🧠 Safety & Settings")
        st.markdown(
            f"""
            <div class="crisis-box">
                <h4>🚨 Immediate Help</h4>
                <p><strong>National Hotline:</strong> {app_config.get('crisis_hotline')}</p>
                <p><strong>Crisis Text:</strong> {app_config.get('crisis_text')}</p>
                <p><strong>Emergency:</strong> Call local emergency services</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="warning-box">
                <h4>⚠️ Important</h4>
                <p>{app_config.get('warning_message')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**OpenAI settings (optional for testing)**")
        # If user provides API key here, it will be placed in environment for the session only.
        api_key_input = st.text_input("OpenAI API Key", type="password", help="Enter API key for testing (or set as Streamlit secret).")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("API key set for this session (not persisted).")

        if st.button("Clear conversation"):
            # Keep the system prompt, reset assistant greeting
            sys_msg = next((m for m in st.session_state.messages if m.get("role") == "system"), None)
            greeting = {
                "role": "assistant",
                "content": f"Conversation cleared. {app_config.get('warning_message')} How can I help you?"
            }
            st.session_state.messages = [sys_msg] if sys_msg else []
            st.session_state.messages.append(greeting)
            st.experimental_rerun()

    # --- Main chat area ---
    st.title(app_config.get("title", "Mental Health Assistant"))
    st.caption("A safe, informational space. Not a replacement for professional care.")

    # Display previous messages (skip system message)
    for msg in st.session_state.messages[1:]:
        role = msg.get("role", "assistant")
        # st.chat_message supports "user" and "assistant", but we keep things simple
        with st.chat_message(role):
            # Use markdown -- ensure message is a string
            content = msg.get("content", "")
            st.markdown(content)

    # Chat input
    user_prompt = st.chat_input("What's on your mind today?")
    if user_prompt:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Crisis handling
        if contains_crisis_keywords(user_prompt):
            ai_text = handle_crisis_response()
        else:
            # Call AI with spinner
            with st.spinner("Thinking..."):
                ai_text = get_ai_response(st.session_state.messages)

        # Append assistant response and display
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        with st.chat_message("assistant"):
            st.markdown(ai_text)

        # Rerun to show the updated chat (preserves input history)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
