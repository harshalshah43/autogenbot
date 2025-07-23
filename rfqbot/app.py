from setup import *

async def main():
    agent_state = None
    result,agent_state = await call_agent("hi",agent_state)
    print(f"AI Assistant: {result.chat_message.content}")
    while True:
        message = input("You:")
        if message!= "quit":
            # result,agent_state = asyncio.run(call_agent(message,agent_state))
            result,agent_state = await call_agent(message,agent_state)
            print(f"AI Assistant: {result.chat_message.content}")

            if "rfq id" in result.chat_message.content.lower():
                agent_state = await agent1.save_state()
                # print(agent_state)
                
                with open(file_to_save, "w") as f:
                    json.dump(agent_state, f, indent=4)
                
                # print(await parse_user_messages(agent_state))
                print("\nSession ended after RFQ was filed.")
                break
            
        else:
            agent_state = await agent1.save_state()
            with open(file_to_save, "w") as f:
                json.dump(agent_state, f, indent=4)
            # print(await parse_user_messages(agent_state))
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