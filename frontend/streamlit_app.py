import streamlit as st
import requests

st.set_page_config(page_title="AI Chatbot", layout="wide")

st.title("🤖 Student AI Chatbot")

# Sidebar with controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Reset button to clear memory
    if st.button("🔄 Clear Chat Memory", use_container_width=True):
        try:
            response = requests.post("http://127.0.0.1:8000/reset-session/")
            if response.status_code == 200:
                st.session_state.messages = []
                st.success("✅ Memory cleared! Starting fresh conversation.")
                st.rerun()
            else:
                pass
        except:
            pass
    
    # Memory status
    if st.button("📊 Check Memory Status", use_container_width=True):
        try:
            response = requests.get("http://127.0.0.1:8000/memory-status/")
            if response.status_code == 200:
                data = response.json()
                st.info(f"""
**Memory Status:**
- Exchanges: {data['memory_exchanges']}
- Size: {data['memory_size_bytes']} bytes
                """)
        except:
            pass
    
    st.markdown("---")
    st.markdown("""
    **Tips for best results:**
    - Ask one question at a time
    - Use "Clear Chat Memory" if responses degrade
    - Be specific about student names
    """)

# chat history store
if "messages" not in st.session_state:
    st.session_state.messages = []

# show old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# input box
if prompt := st.chat_input("Ask something..."):

    # show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # call backend API
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat/",
            json={"query": prompt}
        )

        answer = response.json().get("answer", "No response")

    except:
        answer = "❌ Backend not running"

    # show bot response
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)