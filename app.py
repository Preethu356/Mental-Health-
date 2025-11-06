import streamlit as st
import os
import toml

# Load configuration
config = toml.load("config.toml")
app_config = config["app"]
model_config = config["model"]
style_config = config["style"]

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title=app_config["title"],
    page_icon="🧠",
    layout="centered"
)

# Apply custom CSS
st.markdown(f"""
<style>
    .main {{
        background-color: {style_config["background_color"]};
    }}
    .stChatMessage {{
        padding: 1rem;
    }}
    .warning-box {{
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }}
    .crisis-box {{
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        system_prompt = f"""
        You are a helpful, empathetic mental health information assistant. 
        
        YOUR ROLE:
        - Provide general psychoeducation about mental health topics
        - Offer supportive, validating responses
        - Suggest evidence-based coping strategies
        - Help users understand common mental health concepts
        
        CRITICAL SAFETY RULES:
        - You are NOT a licensed therapist or crisis counselor
        - You cannot provide diagnoses or treatment plans
        - If a user mentions self-harm, suicide, or immediate danger, you MUST:
          1. Acknowledge their pain
          2. Provide the crisis hotline: {app_config['crisis_hotline']}
          3. Encourage them to contact emergency services if in immediate danger
          4. Keep the response brief and focused on safety
        
        Always include this disclaimer in your first response: "{app_config['warning_message']}"
        """
        
        st.session_state.messages = [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"Hello! I'm here to provide general mental health information and support. {app_config['warning_message']} How can I help you today?"}
        ]

def get_ai_response(messages):
    """Get response from OpenAI API"""
    try:
        client = openai.OpenAI(api_key=os.getenv(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))
        
        response = client.chat.completions.create(
            model=model_config["default_model"],
            messages=messages,
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm having trouble responding right now. Please try again later. Error: {str(e)}"

def contains_crisis_keywords(text):
    """Check if user input contains crisis keywords"""
    crisis_keywords = [
        'kill myself', 'suicide', 'end it all', 'want to die',
        'harm myself', 'self harm', 'hurt myself', 'not want to live'
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in crisis_keywords)

def handle_crisis_response():
    """Generate crisis response"""
    return f"""
    I hear that you're in tremendous pain, and I'm deeply concerned about your safety.

    **Please reach out for immediate help:**
    - **Crisis Hotline:** {app_config['crisis_hotline']}
    - **Crisis Text Line:** {app_config['crisis_text']}
    - **Emergency Services:** 911

    You don't have to go through this alone. There are people who want to help you right now.
    """

def main():
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🧠 Safety Info")
        st.markdown(f"""
        <div class="crisis-box">
        <h4>🚨 Immediate Help</h4>
        <p><strong>National Suicide Prevention Lifeline:</strong> {app_config['crisis_hotline']}</p>
        <p><strong>Crisis Text Line:</strong> {app_config['crisis_text']}</p>
        <p><strong>Emergency:</strong> 911</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="warning-box">
        <h4>⚠️ Important</h4>
        <p>{app_config['warning_message']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API key input (for testing - remove in production)
        api_key = st.text_input("OpenAI API Key", type="password", 
                               help="Get your API key from https://platform.openai.com/api-keys")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        if st.button("Clear Conversation"):
            st.session_state.messages = [
                st.session_state.messages[0],
                {"role": "assistant", "content": "Conversation cleared. How can I help you today?"}
            ]
            st.rerun()
    
    # Main chat interface
    st.title(app_config["title"])
    st.caption("A safe space for mental health information and support")
    
    # Display chat messages
    for message in st.session_state.messages[1:]:  # Skip system message
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What's on your mind today?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check for crisis keywords
        if contains_crisis_keywords(prompt):
            ai_response = handle_crisis_response()
        else:
            # Get AI response (only include recent messages to save tokens)
            recent_messages = st.session_state.messages[-6:]  # Last 3 exchanges
            ai_response = get_ai_response(recent_messages)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        # Rerun to update the chat
        st.rerun()
