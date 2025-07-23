import json
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")

import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from autogen_core.tools import FunctionTool

from langchain_google_genai import ChatGoogleGenerativeAI

from nearest_ports import *
from langapp import parse_rfq

# model_client =ChatGoogleGenerativeAI(model='gemini-1.5-flash')
gemini_model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
)

# ollama_model_client = OllamaChatCompletionClient(model="llama3.2")

nearest_port_tool = FunctionTool(get_nearest_ports,description="Tool that gives port suggestions")
find_ports_tool = FunctionTool(find_ports,description='Tool that suggests ports from list of major ports')

agent1 = AssistantAgent(
    name = 'AI_Assistant',
    model_client=gemini_model_client,
    # model_client=ollama_model_client,
    description="A friendly AI agent that files user complaints.",
    system_message=(
        "You are a helpful assistant for customers of a logistics company"
        "You must collect following details:- port of loading, port of delivery, pickup address, delivery address and package summary."
        "If user is not sure of port names, offer port suggestions by making a tool call and extract and provide names from the tool output for the user to choose"
        "You must also collect customer information:- Name,Company Name, Contact Number, Email id"
        "Once the information is collected, generate a random 4-digit number as the RFQ ID, Do not generate RFQ id unless customer information is collected."
        "thank the user, and end the conversation. Do not continue the conversation after collecting all details."
    ),
    tools = [find_ports_tool,nearest_port_tool]
)

async def call_agent(message,agent_state):
    if agent_state:
        await agent1.load_state(agent_state)    
    
    # result = await agent1.run(task=message)
    result = await agent1.on_messages([TextMessage(content = message,source = 'user')],CancellationToken())
    agent_state = await agent1.save_state()
    return result,agent_state

file_to_save = "rfq_data.json"

async def parse_user_messages(agent_state):
    '''This function reads data from json file and concatenates all user messages.'''

    # with open(file_to_save,"r") as f:
    #     data = json.load(f)
    data = agent_state
    messages = data['llm_context']['messages']
    # user_messages = '\n'.join([i['content'] for i in messages if i['type'] == 'UserMessage' or i['type'] == 'AssistantMessage'])
    user_messages = []

    for i in messages:
        if i['type'] in ('UserMessage','AssistantMessage'):
            if isinstance(i.get('content'),str): # If UserMessage is a string
                user_messages.append(i['content'])
    
    user_messages = '\n'.join(user_messages)

    return user_messages

