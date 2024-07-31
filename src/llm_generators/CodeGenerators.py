from dataclasses import dataclass, field
from src.llm_generators.LLMConfig import LLMConfig
from src.semantic_search.semantic_search import SemanticSearch
from src.semantic_search.example_based_prompt_formatter import ExampleBasedPromptFormatter
from src.llm_generators.llm_templates import question_html_gen_template, server_js_template_base, server_py_template_base, solution_html_template
from credentials import api_key
from openai import AsyncOpenAI
import asyncio

@dataclass
class CodeGenerator(LLMConfig):
    base_template: str
    question: str = field(default="", init=False)
    semantic_search: SemanticSearch = field(init=False)
    prompt: str = field(init=False, default="")
    examples: list = field(init=False, default_factory=list)
    client_async: AsyncOpenAI = field(init=False)

    def __post_init__(self):
        self._initialize_semantic_search()
        self._initialize_async_client()

    def _initialize_semantic_search(self):
        self.semantic_search = SemanticSearch(
            csv_path=self.csv_path,
            embedding_column=self.embedding_column,
            embedding_engine=self.embedding_engine,
            search_column=self.search_column,
            output_column=self.output_column,
            n_examples=self.n_examples,
            similarity_threshold=self.similarity_threshold,
            llm_model=self.llm_model,
            temperature=self.temperature,
            embedding_model=self.embedding_model
        )

    def _initialize_async_client(self):
        self.client_async = AsyncOpenAI(api_key=api_key)

    def set_question(self, question: str):
        self.question = question

    def extract_examples(self):
        self.examples = self.semantic_search.extract_examples(self.question)

    def generate_prompt(self, additional_instructions: str = None):
        self.extract_examples()
        template = self.base_template
        if additional_instructions:
            template += additional_instructions
        examples_text = ExampleBasedPromptFormatter.run(
            examples=self.examples,
            template_text=template
        )
        self.prompt = (
            f"{examples_text}\n"
            f"new question: {self.question}\n"
            "Only return the generated code and delimit the generated code with triple backquotes \n"
            "```insert-here```"
        )
        return self.prompt

    async def arun(self, question: str, additional_instructions: str = None):
        self.set_question(question)
        self.generate_prompt(additional_instructions=additional_instructions)
        response = await self.client_async.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are a professor at a University focused on mechanical engineering education."},
                {"role": "user", "content": self.prompt}
            ],
            temperature=self.temperature,
        )
        generated_code = response.choices[0].message.content
        print(f"Generated code for {self.output_column}")
        return generated_code

# Custom Generators
csv_path = r"mechedu1.0\src\data\Question_Embedding_20240128.csv"
question_html_generator = CodeGenerator(
    embedding_column="question_embedding",
    llm_model="gpt-4o",
    embedding_engine="text-embedding-ada-002",
    search_column="question",
    output_column="question.html",
    n_examples=3,
    csv_path=csv_path,
    temperature=0,
    similarity_threshold=0.5,
    embedding_model="text-embedding-ada-002",
    base_template=question_html_gen_template
)

server_js_generator = CodeGenerator(
    embedding_column="question_embedding",
    llm_model="gpt-4o",
    search_column="question.html",
    output_column="server.js",
    n_examples=2,
    csv_path=csv_path,
    temperature=0,
    similarity_threshold=0.5,
    embedding_engine="text-embedding-ada-002",
    embedding_model="text-embedding-ada-002",
    base_template=server_js_template_base
)

server_py_generator = CodeGenerator(
    embedding_column="question_embedding",
    llm_model="gpt-4o",
    search_column="question.html",
    output_column="server.py",
    n_examples=2,
    csv_path=csv_path,
    temperature=0,
    similarity_threshold=0.5,
    embedding_engine="text-embedding-ada-002",
    embedding_model="text-embedding-ada-002",
    base_template=server_py_template_base
)

solution_html_generator = CodeGenerator(
    embedding_column="question_embedding",
    llm_model="gpt-4o",
    search_column="question.html",
    output_column="solution.html",
    n_examples=2,
    csv_path=csv_path,
    temperature=0,
    embedding_model="text-embedding-ada-002",
    embedding_engine="text-embedding-ada-002",
    base_template=solution_html_template,
    similarity_threshold=0.5
)

## Test Implementation
# question = "A ball travels at a distance of 100 miles in 45 minutes along a straight path what is the speed of the ball "
# question_html = asyncio.run(question_html_generator.arun(question))
# print(question_html)
# server_js = asyncio.run(server_js_generator.arun(question_html, f"Please analyze the problem, generate code using the same units as provided in the original question. Ensure all values are properly converted and consistent with the units from the question. Here is the question for reference: {question}"))
# print(server_js)
# server_py = asyncio.run(server_py_generator.arun(question_html))
# print(server_py)
# solution = asyncio.run(solution_html_generator.arun(question_html))
# print(solution)