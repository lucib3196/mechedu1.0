# Standard library imports
import asyncio
import json
from typing import Optional

# Third-party imports
from pydantic import BaseModel, Field

# Langchain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Custom imports
from ...logging_config.logging_config import get_logger

logger = get_logger(__name__)

## Define the LLM and Load the Vector Store
llm = ChatOpenAI(model="gpt-4o-mini")


embedding_function = OpenAIEmbeddings()
vectorstore = Chroma(persist_directory=r"src\llm_module_generator\physics_module_generator\pl_chroma_db", embedding_function=embedding_function)
docs = vectorstore.similarity_search("Matrices")
retriever = vectorstore.as_retriever()
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(), llm=llm
)

## Define the system prompt 
## This will be given to the RAG Chain
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know.If the context provided does not offer information "
    "that directly answers the question, make it clear that the context "
    "does not provide the necessary information."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

## This prompt will go in for the human input of the question
human_prompt = f"""
You have access to documentation on formatting questions using custom HTML tags. Your task is to format user-input questions in a valid format.

For each response, please include:

1. **Analysis**: A brief description of the functionality that the code implements.
2. **Code Snippet**: A short, concise code snippet demonstrating the functionality.

Guidelines:
- Each code snippet should be unique and serve a distinct purpose, avoiding repetition of similar code.
- A single response may contain multiple components if necessary, but aim to be direct and relevant.
- Return a list of potential code implementations. If no suitable implementations are found, return `None`.
- If possible, return the entire formatted HTML. If you're unsure, provide the response in chunks of code snippets.
- Do not generate backend logic; focus solely on front-end components.
- Ensure the entire question they want to convert is handled
- Ensure you adress how the question will be shown to the user and how they will input their answers

Return a maximum of 0-3 analysis and code snippet pairs.

**Question**: {{question}}

Please delimit code snippets using triple backticks: ```.
"""

## Define a structured output for the code
class Code_Analysis(BaseModel):
    """Analyze the code related to the given question."""

    analysis: str = Field(description="A brief description of the functionality that the code implements.")
    code_snippet: str = Field(description="A code snippet delimit the code using triple backticks")

class Response(BaseModel):
    response: Optional[list[Code_Analysis]] = Field(description="A list of potential code implementations based on documentation that matches the given question. If no matches are found, return None.")

## Format the retrieved information
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

## Define the RAG Chain
rag_chain_from_docs = (
    {
        "input": lambda x: x["input"],
        "context": lambda x: format_docs(x["context"]),
    }
    | prompt
    | llm.with_structured_output(Response)
)

retrieve_docs = (lambda x: x["input"]) | retriever_from_llm
chain = RunnablePassthrough.assign(context=retrieve_docs).assign(
    answer=rag_chain_from_docs
)

## Wrap it all in a funciton 

async def pl_code_snippet_chain(question:str)->str:
    code_search = await chain.ainvoke({"input": human_prompt.format(question=question)})
    response_instance = json.loads(code_search["answer"].model_dump_json())
    response = response_instance["response"]
    # Build the example code snippets
    example_code_snippets = "\nThe following are useful code snippets\n"
    for analysis in response:
        anal = analysis.get("analysis")
        code_snippet = analysis.get("code_snippet")
        example_code_snippets += f"\nReasoning to use: {anal}\n Code Snippet: {code_snippet}"
    return example_code_snippets


async def main():
    print(f"Starting analysis: Running Multi Query Retriever {'*'*50}")
    retriever_question = [
    "How to do derivatives using math.js",
    "How do create custom units using mathjs",
    "How to create symbolic expressions"]

    for question in retriever_question:
        print(f"Starting analysis on question :{question}\n{'*'*50}\n")
        print(retriever_from_llm.get_relevant_documents(question))
        print()
    print(f"Starting analysis: Running RAG Chain {'*'*50}")

    code_questions = [
    "Calculate the eigenvalues and eigenvectors of the matrix A = [[2, 1], [1, 3]].",
    "Given the function f(x) = 3x^2 - 2x + 5, compute the derivative f'(x) and evaluate it at x = 4.",
    "A projectile is launched at an angle of 45° with an initial velocity of 20 m/s. Compute the time of flight and the maximum height."]

    for question in code_questions:
        print(f"Starting analysis on question :{question}\n{'*'*50}\n")
        print(await pl_code_snippet_chain(question))
        print()
if __name__ =="__main__":
    asyncio.run(main())



