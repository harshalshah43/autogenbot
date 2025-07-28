import streamlit as st
from setup import *
from langapp import parse_rfq,parse_user_messages

# Streamlit app
st.title("🧠 AI RFQ Agent")

# Initialize session state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

# Input message
user_input = st.chat_input("Enter your message:", key="user_input")


if user_input:
    with st.spinner("Thinking..."):
        # Run the async call inside Streamlit
        response, updated_state = asyncio.run(call_agent(user_input, st.session_state.agent_state))

        st.markdown(f"AI Assistant: {response.chat_message.content}")
        
        # Update session state
        st.session_state.agent_state = updated_state
