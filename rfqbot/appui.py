import streamlit as st
import atexit
from setup import *
from langapp import parse_rfq, parse_user_messages

# -------------------- App Settings --------------------
st.set_page_config(page_title="AI RFQ Agent", page_icon="🧠", layout="wide")
st.title("🧠 Welcome to Your RFQ Assistant")

# Add custom font style
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Calibri', sans-serif !important;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- Session Initialization --------------------
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

# -------------------- Show Previous Messages --------------------
if st.session_state.agent_state is not None:
    messages = st.session_state.agent_state['llm_context']['messages']
    for msg in messages:
        if msg['type'] == 'UserMessage' and isinstance(msg.get('content'), str):
            with st.chat_message("User", avatar="👤"):
                st.markdown(msg['content'])
        elif msg['type'] == 'AssistantMessage' and isinstance(msg.get('content'), str):
            with st.chat_message("AI", avatar="🤖"):
                st.markdown(msg['content'])
        elif msg['type'] == 'FunctionExecutionResultMessage':
            if isinstance(msg.get('content'), list) and msg['content']:
                with st.chat_message("AI", avatar="🤖"):
                    st.markdown(msg['content'][0]['content'])

# -------------------- Chat Input --------------------
user_input = st.chat_input("Type your RFQ details here")

if user_input:
    lower_input = user_input.strip().lower()

    # ✅ Handle reset commands from chat
    if lower_input in 'quit':
        st.session_state.agent_state = None
        st.session_state.chat_history = []
        st.session_state.session_ended = False
        st.rerun()

    # ✅ Otherwise proceed normally
    else:
        with st.spinner("Thinking... Please wait..."):
            response, agent_state = asyncio.run(call_agent(user_input, st.session_state.agent_state,agent1))
            st.session_state.agent_state = agent_state

            if response.chat_message.type == "TextMessage":
                if "RFQ has been filed. This session is now complete." in response.chat_message.content:
                    save_conversation(agent_state, full_client_conversation)
                    rfq_dict = parse_rfq(asyncio.run(parse_user_messages(agent_state)))
                    save_rfq(rfq_dict, rfq_filename)

                    with st.chat_message('AI',avatar = '🤖'):
                        st.markdown("Session ended after RFQ was filed.")
                        st.markdown("If you wish to file another RFQ, enter YES else type quit")

        st.rerun()

# -------------------- Manual Reset Button --------------------
if st.button("🔄 Start Over"):
    st.session_state.agent_state = None
    st.session_state.chat_history = []
    st.session_state.session_ended = False
    st.rerun()


# -------------------- Shutdown Cleanup --------------------
@atexit.register
def shutdown():
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(gemini_model_client.close())
        loop.close()
    except Exception as e:
        print("Error closing model client:", e)
