import streamlit as st
from setup import *


# Initialize session state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_ended" not in st.session_state:
    st.session_state.session_ended = False

# Title
st.title("📦 Logistics AI Assistant (RFQ Generator)")

# Show chat history
for speaker, msg in st.session_state.chat_history:
    if speaker == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)

# Async call handler using asyncio coroutine
async def handle_message(message):
    result, st.session_state.agent_state = await call_agent(message, st.session_state.agent_state)
    st.session_state.chat_history.append(("user", message))
    st.session_state.chat_history.append(("assistant", result.chat_message.content))

    if "rfq id" in result.chat_message.content.lower():
        st.session_state.session_ended = True

        agent_state = await agent1.save_state()
        with open(file_to_save, "w") as f:
            json.dump(agent_state, f, indent=4)

        user_messages = await parse_user_messages(agent_state)
        rfq = parse_rfq(user_messages)
        with open("rfq.json", "w") as f:
            json.dump(rfq, f, indent=4)

        st.success("RFQ filed successfully ✅")
        st.json(rfq)

# Use chat input
if not st.session_state.session_ended:
    user_input = st.chat_input("Enter your message...")
    if user_input:
        asyncio.run(handle_message(user_input))  # This works inside a single block cleanly

else:
    st.warning("Session ended. Refresh to start a new one.")


if st.button("🔄 Reset Chat"):
    st.session_state.agent_state = None
    st.session_state.chat_history = []
    st.session_state.session_ended = False
    st.rerun()
