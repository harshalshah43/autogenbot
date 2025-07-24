from setup import *
from langapp import parse_rfq

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

async def main():
    agent_state = None
    response,agent_state = await call_agent("hi",agent_state)
    print(f"AI Assistant: {response.chat_message.content}")
    while True:
        message = input("Yo" \
        "u:")
        if message!= "quit":
            response,agent_state = await call_agent(message,agent_state)
            print(f"AI Assistant: {response.chat_message.content}")

            if "rfq id" in response.chat_message.content.lower():
                agent_state = await agent1.save_state()
                
                with open(file_to_save, "w") as f:
                    json.dump(agent_state, f, indent=4)
                
                print("\nSession ended after RFQ was filed.")
                break
            
        else:
            agent_state = await agent1.save_state()
            with open(file_to_save, "w") as f:
                json.dump(agent_state, f, indent=4)
            # print(await sparse_user_messages(agent_state))
            break
    
    print(parse_rfq(await parse_user_messages(agent_state)))
    with open("rfq.json", "w") as f:
        json.dump(parse_rfq(await parse_user_messages(agent_state)), f, indent=4)

# Driver Code
if __name__ == "__main__":
    asyncio.run(main()) 


# Post suggestions
# Package Summary:- GP Containers, you dont need dimensions only weight per container.
# Special Purpose Containers, you need dimensions and weights.
# For break bulk, we need dims, CBM (volume) or FRT (Freight Ton) i.e max of total CBM and total weight

# Update existing RFQs
# DG/ Hazardous Cargo