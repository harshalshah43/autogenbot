import atexit
from setup import *
from langapp import parse_rfq,parse_user_messages
import asyncio

# Streamlit app
st.title("🧠 Register your RFQ with us here.")

# Initialize session state
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None

# Displaying conversation history if there is one
if st.session_state.agent_state is not None:
    data = st.session_state.agent_state
    messages = data['llm_context']['messages']
    for i in messages:
        if i['type'] == 'UserMessage':
            if isinstance(i.get('content'),str):
                with st.chat_message('You',avatar = '👤'):
                    st.markdown(f"{i['content']}")
        if i['type'] == 'AssistantMessage':
            if isinstance(i.get('content'),str):
                with st.chat_message('You',avatar = '🤖'):
                    st.markdown(f"{i['content']}")
        if i['type'] == 'FunctionExecutionResultMessage':
            if isinstance(i.get('content'),list):
                if i['content']: # if list is not empty
                    with st.chat_message('AI',avatar = '🤖'):
                        st.markdown(f"{i['content'][0]['content']}")


if st.button("🔄 Reset Chat"):
    st.session_state.agent_state = None
    st.session_state.chat_history = []
    st.session_state.session_ended = False
    agent_state,agent1 = None,None
    agent1 = initialize_agent()
    
    # asyncio.run(gemini_model_client.close())
    st.rerun()
    


# Input message
user_input = st.chat_input("Enter your message:", key="user_input")


if user_input:
    if user_input.lower().strip() != 'quit':
        with st.spinner("Thinking..."):
            # Run the async call inside Streamlit
            response, agent_state = asyncio.run(call_agent(user_input, st.session_state.agent_state,agent1))
            
            st.session_state.agent_state = agent_state
            
            if response.chat_message.type == "TextMessage":
                if "RFQ has been filed. This session is now complete." in response.chat_message.content:

                    save_conversation(st.session_state.agent_state,full_client_conversation)
                    
                    rfq_dict = parse_rfq(asyncio.run(parse_user_messages(agent_state)))
                    
                    save_rfq(rfq_dict,rfq_filename)

                    with st.chat_message('AI',avatar = '🤖'):
                        st.markdown("Session ended after RFQ was filed.")
                        st.markdown("If you wish to file another rfq, enter YES else type quit")
                

                # st.session_state.agent_state = None
                # st.session_state.chat_history = []
                # st.session_state.session_ended = False
    # asyncio.run(gemini_model_client.close())
    st.rerun()




@atexit.register
def shutdown():
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(gemini_model_client.close())
        loop.close()
    except Exception as e:
        print("Error closing model client:", e)
