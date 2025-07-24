from langchain_core.output_parsers import StrOutputParser,JsonOutputParser
from langchain.prompts import PromptTemplate,ChatPromptTemplate
from typing import TypedDict, Annotated, Sequence, Optional
from pydantic import BaseModel,Field
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional,List,Annotated
from pydantic import BaseModel, Field, field_validator,StringConstraints

Stripped = Annotated[str, StringConstraints(strip_whitespace=True)]
StrippedPhone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20)]

model_name = 'gemini-2.0-flash'
llm=ChatGoogleGenerativeAI(model=model_name)

class RFQState(BaseModel):
    pol: Optional[List[Stripped]] = Field(
        default=None,
        description="Origin ports/airports only (e.g., Jebel Ali, Shanghai). Exclude pickup cities or regions."
    )
    pod: Optional[List[Stripped]] = Field(
        default=None,
        description="Destination ports/airports only (e.g., Nhava Sheva, JFK). Exclude delivery locations."
    )
    contact_names: Optional[List[Stripped]] = Field(
        default=None,
        description="Names from thread, headers, or signature."
    )
    contact_numbers: Optional[List[StrippedPhone]] = Field(
        default=None,
        description="Valid contact numbers. Infer if clear."
    )
    pickup_addresses: Optional[List[Stripped]] = Field(
        default=None,
        description="Pickup/Supplier's pickup address (street/city/country only). Exclude port names and unrelated signature content"
    )
    delivery_addresses: Optional[List[Stripped]] = Field(
        default=None,
        description=(
            "Delivery/Consignee's address (street/city/country only). Exclude port names and unrelated signature content"
        )
    )
    package_summary: Optional[Stripped] = Field(
        default=None,
        description="Package summary from subject/body"
    )

    rfq_id: str = None

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

def parse_rfq(human_message) -> dict:
    """Call this tool only when user has provided all logistics information.
    Use this tool to extract user's port of loading, port of delivery, pickup address, delivery address and package summary. 
    Also extract:-customer information:- Name,Company Name, Contact Number, Email id from human messages."""

    template="""
    Extract logistics information from User Query such as:- port of loading, port of delivery, pickup address, delivery address and package summary. 
    Also extract customer information from User Query such as:- Name, Company Name, Contact Number, Email id and RFQ id.
    User query: {question}
    {format_instructions}
    """
    parser = JsonOutputParser(pydantic_object=RFQState)
    prompt= PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt | llm | parser
    response = chain.invoke({
        'question':human_message
    })

    return response
