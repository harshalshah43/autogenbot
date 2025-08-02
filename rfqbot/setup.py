import json
import os
import datetime
from prompts import *

import asyncio
from dotenv import load_dotenv
load_dotenv()

from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen_ext.models.ollama import OllamaChatCompletionClient

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from autogen_core.tools import FunctionTool

# from langchain_google_genai import ChatGoogleGenerativeAI

from tool_functions import *

# model_client =ChatGoogleGenerativeAI(model='gemini-1.5-flash')
gemini_model_client = OpenAIChatCompletionClient(
    model="gemini-2.5-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
    max_tokens = 4096
)

# ollama_model_client = OllamaChatCompletionClient(model="llama3.2")

# nearest_port_tool = FunctionTool(get_nearest_ports,description="Tool that gives port suggestions by calling geoapify api")
find_ports_tool = FunctionTool(find_ports,description='Tool uses fuzzy logic to get ports in a particular city or country')

async def call_agent(message,agent_state,agent1):
    if agent_state:
        await agent1.load_state(agent_state)
    else:
        await agent1.on_reset(agent_state)
    
    # result = await agent1.run(task=message)
    response = await agent1.on_messages([TextMessage(content = message,source = 'user')],CancellationToken())
    agent_state = await agent1.save_state()
    return response,agent_state

full_client_conversation = "conversations/chat_{}.json"
rfq_filename = "rfqs/rfq_{}.json"

def save_conversation(agent_state,filename = "conversations/conv_{}.json"):
    datetime_str = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S").replace(":","_")
    if agent_state is not None:
        os.makedirs('conversations', exist_ok=True)
        with open(filename.format(datetime_str), "w") as f:
            json.dump(agent_state, f, indent=4)
            print("file saved")
    else:
        print("not saved")
    
def save_rfq(data,filename = "rfqs/rfq_{}.json"):
    datetime_str = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M:%S").replace(":","_")
    if data is not None:
        rfq_id = data.get("rfq_id","")
        os.makedirs('rfqs', exist_ok=True)
        with open(filename.format(datetime_str + "_" + rfq_id), "w") as f:
            json.dump(data, f, indent=4)
            print("file saved")
    else:
        print("not saved")