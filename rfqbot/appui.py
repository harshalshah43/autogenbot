import streamlit as st
import asyncio
import json
import os
from dotenv import load_dotenv
load_dotenv()

from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_google_genai import ChatGoogleGenerativeAI
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from autogen.rfqbot.langapp import parse_rfq



st.set_page_config(page_title="AI Logistics Assistant", layout="centered")

# --- Setup model and agent ---
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
)

agent1 = AssistantAgent(
    name='AI_Assistant',
    model_client=model_client,
    description="A friendly AI agent that files user complaints.",
    system_message=(
        "You are a helpful assistant for customers of a logistics company. "
        "Do the following step by step in a conversational manner. "
        "You must collect the following details: port of loading, port of delivery, pickup address, delivery address, and package summary. "
        "You must also collect customer information: Name, Company Name, Contact Number, Email ID. "
        "Once the information is collected, generate a random 4-digit number as the RFQ ID. "
        "Do not generate the RFQ ID unless customer information is collected. "
        "Thank the user and end the conversation. Do not continue the conversation after collecting all details."
    ),
)

# --- Session state ---
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rfq_saved" not in st.session_state:
    st.session_state.rfq_saved = False

file_to_save = "rfq_data.json"

async def call_agent(message, agent_state):
    if agent_state:
        await agent1.load_state(agent_state)
    result = await agent1.on_messages([TextMessage(content=message, source="user")], CancellationToken())
    agent_state = await agent1.save_state()
    return result, agent_state

async def parse_user_messages(agent_state):
    messages = agent_state['llm_context']['messages']
    user_messages = '\n'.join([i['content'] for i in messages])
    return user_messages

# --- App Layout ---
st.title("📦 AI Logistics Assistant")
st.markdown("Chat with the assistant to file your shipping request.")

# --- 1. Chat history first ---
for sender, message in st.session_state.chat_history:
    if sender == "You":
        st.chat_message("user").markdown(message)
    else:
        st.chat_message("assistant").markdown(message)

# --- 2. Then user input form ---
if not st.session_state.rfq_saved:
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:", "")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        async def process_message():
            result, updated_state = await call_agent(user_input, st.session_state.agent_state)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", result.chat_message.content))
            st.session_state.agent_state = updated_state

            if "rfq id" in result.chat_message.content.lower():
                with open(file_to_save, "w") as f:
                    json.dump(updated_state, f, indent=4)

                messages_text = await parse_user_messages(updated_state)
                parsed_data = parse_rfq(messages_text)

                with open("rfq.json", "w") as f:
                    json.dump(parsed_data, f, indent=4)

                st.session_state.rfq_saved = True
                st.success("✅ RFQ filed and saved to `rfq.json`. Session ended.")

        asyncio.run(process_message())
else:
    st.info("🔒 RFQ session ended. Reload the page to start a new session.")
