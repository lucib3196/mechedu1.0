from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from pydantic import BaseModel, Field
from typing import Optional, Union, List
import asyncio

# Pull the prompt for the quiz module query analyzer
prompt = hub.pull("pollytheparot69/quiz_module_query_analyzer_refiner")

class Metadata(BaseModel):
    generated: bool = Field(description="Indicate if the question is generated True or given False")

# Define the ModuleSpecification model
class ModuleSpecification(BaseModel):
    """Specification for Module"""
    question: str = Field(description="The question to be generated")
    question_html_instructions: Optional[Union[bool, str]] = Field(description="Any question html instructions such as styling or type these need to be explitly stated")
    server_instructions: Optional[Union[bool, str]] = Field(description="server requirements these should be explitly stated")
    metadata: Metadata

# Set up the model and chain with structured output
model = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | model.with_structured_output(ModuleSpecification)

# Define the MetaData model
class ModuleMetaData(BaseModel):
    title: str = Field(..., description="An appropriate title for the given question, returned using CamelCase format")
    stem: str = Field(..., description="Additional context or a subtopic related to the main topic")
    topic: str = Field(..., description="The main topic or subject of the educational content")
    tags: List[str] = Field(..., description="An array of keywords or tags associated with the content")
    prereqs: List[str] = Field(..., description="An array of prerequisites needed to access or understand the content")
    isAdaptive: bool = Field(..., description="Designates whether the content necessitates any form of numerical computation")

# Define the Response model
class Response(BaseModel):
    question: str = Field(..., description="The original question that was classified")
    metadata: ModuleMetaData

# Pull the metadata prompt
metadata_prompt = hub.pull("gestalt_metadata")
# Set up the metadata chain
metadata_model = ChatOpenAI(model="gpt-4o-mini")
metadata_chain = metadata_prompt | metadata_model.with_structured_output(Response)



# Main async function
async def main():
    # Invoke the main chain with the initial query
    data = await chain.ainvoke({"query": "I want to generate the following 'A car is traveling at a distance of 60 mph for 5 hours, what is the total distance traveled.' I want to ensure that there are a variety of units in the calculations including ft/s, mph and kmh for the speeds"})
    data = data.dict()
    question = data.get("question")
    metadata_chain.invoke({"question":question})
# Run the main async function
if __name__ == "__main__":
    asyncio.run(main())