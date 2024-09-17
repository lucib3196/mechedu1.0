import asyncio
from src.llm_module_generator.llm_base import LLMConfig
from ...credentials import api_key
from ..ui_generator.ui_builder import LLMUIBuilder
from ..physics_module_generator.module_generator import ModuleCodeGenerator
from dataclasses import dataclass, field
from ..physics_module_generator.llm_templates import question_html_gen_template
from ...data_handler.example_based_prompt_formatter import ExampleBasedPromptDataFrame
import pandas as pd
from pydantic import BaseModel, Field
import os 
from ...logging_config.logging_config import get_logger
from .question_html_response import UI
from ast import literal_eval
# Initialize logger
logger = get_logger(__name__)


class TagResponse(BaseModel):
  element_name:str = Field(...,description="The name of the element")
  reasoning:str = Field(...,description = "The reasoning behind why this element is appropriate for the given question")
class Response(BaseModel):
  analysis: str = Field(...,description="An analysis of what is required to make the given question into an online format quiz")
  tags: list[TagResponse] = Field(..., description="A list of tags appropriate for the given question")
# Set base directory and path to the CSS styles file
base_dir = os.path.dirname(os.path.abspath(__file__))
element_data = os.path.join(base_dir, 'element_data.csv')


@dataclass
class QuestionHTMLBuilder(ModuleCodeGenerator,LLMUIBuilder):
    def __post_init__(self):
        self.example_formatter = ExampleBasedPromptDataFrame(
            example_input_column=self.example_input_column,
            example_output_column=self.example_output_column,
            api_key=self.llm_config.api_key,
            is_adaptive=self.is_adaptive
        )
        # Assuming element_data is defined elsewhere
        self.df = pd.read_csv(element_data)
        return super().__post_init__()
    def get_element_description(self)->str:
        all_description =""
        for i in range(len(self.df["short_description"])):
            all_description += f'\n{self.df["short_description"][i]}'
        return all_description
    
    async def analyze_question(self,question:str):
       all_descriptions = self.get_element_description()
       prompt = f"""
        You are tasked with converting the following question into an online quiz format. Your analysis should cover the following aspects and include reasoning for each tag you choose:

        1. **Question Type**: Identify the type of question (e.g., multiple choice, short answer, numeric input, etc.).
        2. **Student Input Format**: Define how the student is expected to interact with the question (e.g., selecting from options, entering numbers, typing text).
        3. **Adaptation for Online Assessment**: Explain how the question can be formatted for an online quiz. This includes considerations such as formatting requirements, numeric input tolerances, or opportunities for partial credit.
        4. **Special Considerations**: Highlight any special elements (e.g., diagrams, formulas, or complex inputs) that may impact the design of the quiz.

        Additionally, your analysis must reference the following custom HTML tags: {all_descriptions}. These tags will be used when converting the question into an online assessment. 

        For each tag you select, provide reasoning as to why it is useful for the quiz construction.

        The question to analyze is: {question}

        In your response, return:
        - A list of the most relevant HTML tag names that will aid in constructing the question for an online quiz.
        - Brief reasoning behind each tag choice to clarify its importance in the context of the question.
        - Only return valid tag names; do not include any HTML formatting.
        """
       response = await self.acall(prompt, response_format=Response) # type: ignore
       return response
    def extract_example_questions_html(self, element_name: str) -> str:
        try:
            # Filter the dataframe based on the element name and reset the index
            filtered_df = self.df[self.df["element_name"] == element_name].reset_index()
            filtered_df["question_data"] = filtered_df["question_data"].apply(literal_eval)
            # Check if the dataframe is empty
            if filtered_df.empty:
                logger.error(f"No matching rows found for element name: {element_name}")
                return ""

            # Get the first 'question_data' entry from the filtered dataframe
            example = filtered_df["question_data"][0]

            # If 'question_data' is a list, process each entry
            if isinstance(example, list):
                if not example:
                    logger.warning(f"Empty list found for 'question_data' in element: {element_name}")
                    return ""

                examples = ""
                for ex in example:
                    examples += f"\n{ex['question_html']}"
                return examples

            # If 'question_data' is a string, check if it's valid HTML
            elif isinstance(example, str):
                return example["question_html"]

            # Handle unexpected types for 'question_data'
            else:
                logger.error(f"Unexpected type for 'question_data' in element: {element_name}")
                return ""

        except KeyError as e:
            logger.error(f"KeyError: Missing expected column or key - {e}")
            return ""

        except IndexError as e:
            logger.error(f"IndexError: Issue accessing 'question_data' - {e}")
            return ""

        except Exception as e:
            logger.error(f"An unexpected error occurred while processing element: {element_name} - {e}")
            return ""
        
    def get_element_instructions(self,response:dict)->str:
        instructions = ""
        analysis = response.get("analysis","")
        instructions +=  f"Analysis: {analysis}\n"
        tags = response.get("tags","")
        for tag in tags:
            element_name = tag.get("element_name")
            element_name = element_name.replace("<","")
            element_name = element_name.replace(">","")
            reasoning = tag.get("reasoning")
            example_questions_html = self.extract_example_questions_html(element_name)

            instructions+=f"Element Name: {element_name}\nReasoning: {reasoning}\nTag Examples: {example_questions_html}\n\n"
        return instructions
    
    async def generate_html_ui(self,question:str):
        analysis_response = await self.analyze_question(question)
        instructions = self.get_element_instructions(analysis_response) # type: ignore
        prompt = self.generate_prompt(question,additional_instructions=instructions)
        with open(r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\llm_module_generator\question_html_ui\prompt.txt",'w',encoding="utf-8") as f:
            f.write(prompt)
        question_html = await self.generate_ui(prompt, ui_instance=UI)
        return question_html

llm_config = LLMConfig(api_key=api_key,model = "gpt-4o-2024-08-06",temperature=0) # type: ignore
question_html_builder_advance = QuestionHTMLBuilder(
llm_config=llm_config,
base_prompt=question_html_gen_template,
example_input_column="question",
example_output_column="question.html",css_category="",num_examples=1,threshold=0.4)

async def main(question:str):
   llm_config = LLMConfig(api_key=api_key,model = "gpt-4o-2024-08-06",temperature=0) # type: ignore
   question_html_builder = QuestionHTMLBuilder(
    llm_config=llm_config,
    base_prompt=question_html_gen_template,
    example_input_column="question",
    example_output_column="question.html",css_category="",num_examples=1,threshold=0.7)
   
   return await question_html_builder.generate_html_ui(question)
   
if __name__ == "__main__":
   question = r"""
    You are tasked with analyzing a simple truss bridge consisting of three members and three nodes. The bridge is subject to a vertical load and requires careful calculation to ensure structural stability. The truss consists of the following nodes:

    - Node 1 at (0, 0)
    - Node 2 at (4, 0)
    - Node 3 at (4, 3)

    A vertical load of **500 N** is applied at Node 3.

    ---

    #### Part 1: Global Stiffness Matrix Assembly (Matrix Input)

    You are provided with the local stiffness matrices for each member of the truss. Use these matrices to assemble the global stiffness matrix for the entire system.

    - Element 1 (between Node 1 and Node 2):  
    K_1 = [[300, -300], [-300, 300]]

    - Element 2 (between Node 2 and Node 3):  
    K_2 = [[500, -500], [-500, 500]]

    - Element 3 (between Node 1 and Node 3):  
    K_3 = [[400, -400], [-400, 400]]

    **Input:**
    - Provide the **assembled global stiffness matrix** for the entire truss system.

    ---

    #### Part 2: Displacement at Node 3 (Numeric Input with Units)

    Using the global stiffness matrix from Part 1, calculate the vertical displacement at Node 3 under the applied 500 N vertical load. The members are made of steel with a Young's modulus of E = 210 GPa.

    **Formula:**
    Displacement, Δ = F / K

    **Input:**
    - Enter the displacement at Node 3 in **millimeters (mm)**.

    ---

    #### Part 3: Stress in Each Member (Number Input with Units)

    For each truss member, calculate the axial stress under the applied load. Assume the cross-sectional area of each member is **50 mm²**.

    **Formula:**
    Stress, σ = F / A

    **Input:**
    - Enter the stress in each member in **N/mm² (MPa)** for the following:
    - **Member 1 (Node 1 to Node 2)**: _______ MPa
    - **Member 2 (Node 2 to Node 3)**: _______ MPa
    - **Member 3 (Node 1 to Node 3)**: _______ MPa

    ---

    #### Part 4: Match the Components (Matching Input)

    Match the following truss bridge components to their correct definitions:

    | Component      | Definition                                              |
    |----------------|---------------------------------------------------------|
    | **Nodes**      | A. The points where two or more members meet            |
    | **Members**    | B. Structural elements that carry tensile or compressive forces |
    | **Stiffness**  | C. A property that defines how much a structure resists deformation |
    | **Stress**     | D. Internal force per unit area within a material       |

    **Input:**
    - Match each component with the correct definition by selecting the appropriate letter.
    """
   result = asyncio.run(main(question))
   print(result)
