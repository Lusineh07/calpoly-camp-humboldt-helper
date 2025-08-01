# streamlit.py
import streamlit as st
import os
import base64
from main import query_bedrock, build_history, KB_IDS, handle_small_talk

# --- Page Setup ---
st.set_page_config(page_title="Humboldt Helper", layout="wide")

# --- Load CSS ---
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Image Handling ---
def get_base64_image(path):
    try:
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return ""

base_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(base_dir, "images")

logo_base64 = get_base64_image(os.path.join(img_dir, "Logo.png"))
user_icon = get_base64_image(os.path.join(img_dir, "user_icon.png"))
bot_icon = get_base64_image(os.path.join(img_dir, "robot_icon.png"))

# --- Sidebar HTML ---
st.markdown(f"""
<div class="fixed-sidebar">
    <div style="text-align: center; margin-top: 2rem; margin-bottom: 2.5rem;">
        <img src="data:image/png;base64,{logo_base64}" style="width: 240px;" />
    </div>
    <p>Welcome to Humboldt Helper, your AI guide to find the right files, links, and information across the California State Polytechnic University, Humboldt Office of Research.</p>
    <p><em>Need help? Just Ask!</em></p>
</div>
""", unsafe_allow_html=True)

# --- App Header ---
st.markdown("""
<div class="main-content">
    <div class="main-title">Humboldt Helper</div>
    <div class="subtitle">Let the exploration begin.</div>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! I’m Humboldt Helper. I can help you locate research documents, funding opportunities, and resources regarding research. How can I assist you?"
    }]
# --- Show Chat History ---
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    avatar = user_icon if is_user else bot_icon
    css_class = "message-user" if is_user else "message-assistant"
    sender = "You" if is_user else "Humboldt Helper"
    alignment = "flex-end" if is_user else "flex-start"
    avatar_html = f'<img src="data:image/png;base64,{avatar}" style="width: 32px; height: 32px;">'

    if is_user:
        # User message on right
        st.markdown(f"""
        <div class="message-bubble" style="justify-content: {alignment}; display: flex;">
            <div style="max-width: 70%; text-align: right;" class="message-content {css_class}">
                <div style="font-size: 13px; font-weight: bold;">{sender}</div>
                <div style="font-size: 14px; font-family: Inter, sans-serif;">{msg["content"]}</div>
            </div>
            <div style="margin-left: 0.75rem;">{avatar_html}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Assistant message on left
        st.markdown(f"""
        <div class="message-bubble" style="justify-content: {alignment}; display: flex;">
            <div style="margin-right: 0.75rem;">{avatar_html}</div>
            <div style="max-width: 70%;" class="message-content {css_class}">
                <div style="font-size: 13px; font-weight: bold;">{sender}</div>
                <div style="font-size: 14px; font-family: Inter, sans-serif;">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- Padding so messages are not hidden behind input bar
st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True)

# --- Chat Input (fixed bottom) ---
prompt = st.chat_input("Ask a question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        small_talk_reply = handle_small_talk(prompt)

        if small_talk_reply:
            response, refs = small_talk_reply, []
        else:
            chat_history = build_history(st.session_state.messages, prompt)
            response, refs = query_bedrock(prompt, chat_history)


    full_response = response
    if refs:
        full_response += "\n\n---\n**References**\n" + "\n".join(refs)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

    # Rerun immediately to show updated message list with custom styling
    st.rerun()
