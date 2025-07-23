import asyncio
from autogen_ext.models.openai import OpenAIChatCompletionClient
from langchain_google_genai import ChatGoogleGenerativeAI
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage

from dotenv import load_dotenv
import os
load_dotenv()

import json

model_client =ChatGoogleGenerativeAI(model='gemini-1.5-flash')
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.environ.get("GOOGLE_API_KEY"),
)


agent1 = AssistantAgent(
    name = 'AI_Assistant',
    model_client=model_client,
    description="A friendly AI agent that files user complaints.",
    system_message=(
        "You are a helpful assistant whose job is to collect the user's full name, email, and phone number. "
        "You must also ask the user to briefly describe their complaint."
        "Once all this information is collected, generate a random 4-digit number as the complaint ID, "
        "thank the user, and end the conversation. Do not continue the conversation after collecting all details."
    ),
)

async def call_agent(message,agent_state):
    if agent_state:
        await agent1.load_state(agent_state)    
    
    # result = await agent1.run(task=message)
    result = await agent1.on_messages([TextMessage(content = message,source = 'user')],CancellationToken())
    agent_state = await agent1.save_state()
    return result,agent_state


async def main():
    agent_state = None
    while True:
        message = input("You:")
        if message!= "quit":
            # result,agent_state = asyncio.run(call_agent(message,agent_state))
            result,agent_state = await call_agent(message,agent_state)
            print(f"AI Assistant: {result.chat_message.content}")

            if "complaint ID" in result.chat_message.content.lower():
                print("\nSession ended after complaint was filed.")
                agent_state = await agent1.save_state()
                print(agent_state)
                with open("data.json", "w") as f:
                    json.dump(agent_state, f, indent=4)
                break
            
        else:
            agent_state = await agent1.save_state()
            print(agent_state)
            with open("data.json", "w") as f:
                json.dump(agent_state, f, indent=4)
            break

asyncio.run(main())

