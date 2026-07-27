import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file immediately
load_dotenv()

# Skylark Drones official logo URL (or replace with local path "assets/skylark_logo.png")
SKYLARK_LOGO_URL = "Sky.png"

st.set_page_config(
    page_title="Skylark Drones - Leadership BI Agent",
    page_icon=SKYLARK_LOGO_URL,
    layout="wide"
)

# Render logo in the sidebar if supported in your Streamlit version
try:
    st.logo(SKYLARK_LOGO_URL, icon_image=SKYLARK_LOGO_URL)
except AttributeError:
    pass

# Header Section with Logo
col1, col2 = st.columns([1, 8])
with col1:
    try:
        st.image(SKYLARK_LOGO_URL, width=80)
    except Exception:
        st.text("🚁")
with col2:
    st.title("Skylark Drones - Executive BI Agent")
    st.caption("Powered by monday.com GraphQL API & Groq")

def get_secret(key_name: str) -> str:
    """Checks os.environ (.env), falls back to Streamlit secrets, then empty string."""
    val = os.getenv(key_name)
    if val:
        return val
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return ""

# Retrieve keys reliably from .env
groq_key = get_secret("GROQ_API_KEY")
monday_token = get_secret("MONDAY_API_TOKEN")

with st.sidebar:
    st.header("⚙️ System Status")
    
    if groq_key and monday_token:
        st.success("API Credentials Active (Loaded from .env)")
    else:
        st.warning("Missing API Keys. Enter them below or ensure .env is in the project root.")
        groq_key = st.text_input("Groq API Key", type="password", value=groq_key)
        monday_token = st.text_input("Monday API Token", type="password", value=monday_token)
        
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.subheader("💡 Sample Founder Queries")
    st.markdown("- *How is our deal pipeline looking for the energy sector?*")
    st.markdown("- *Are there any delayed work orders?*")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Process User Input
if prompt := st.chat_input("Ask an executive business question..."):
    if not groq_key or not monday_token:
        st.error("Please provide API keys!")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing live business data..."):
            try:
                from agent import BIAgent
                agent = BIAgent(monday_token=monday_token, groq_key=groq_key)
                
                clean_history = [
                    {"role": m["role"], "content": m["content"][:300]}
                    for m in st.session_state.messages[:-1]
                    if m.get("role") in ["user", "assistant"] and isinstance(m.get("content"), str)
                ][-2:]
                
                response = agent.run(prompt, chat_history=clean_history)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")