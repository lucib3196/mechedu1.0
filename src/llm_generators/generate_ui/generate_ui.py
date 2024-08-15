from openai import AsyncOpenAI
from pydantic import BaseModel, Field,validator
import json
from typing import List
import asyncio
from ...credentials import api_key
from .get_valid_css import get_valid_css_classes
from .ui_type import UIType

async def generate_and_return_ui(prompt:str, css_name_interst:str = ""):
    client_async = AsyncOpenAI(api_key=api_key)
    VALID_CSS_STYLES, css_descriptions = get_valid_css_classes(css_name_interst, UIType)

    class Attribute(BaseModel):
        name: str = Field(..., description="Name of html attribute")
        value: str = Field(..., description="Value of the html attribute ")
    class UI(BaseModel):
        type: UIType
        label: str = Field(...,description="Content to be placed inside HTML tags. If you need to write mathematical symbols or equations, use LaTeX enclosed within `$...$` for inline math or `$$...$$` for display math to ensure compatibility with the HTML file.")
        children: List["UI"]
        attributes: List[Attribute]
        
        @validator('attributes', each_item=True)
        def validate_attributes(cls, attr, values):
                ui_type = values.get('type')
                # print(attr.name)
                # print(f"This is the ui type {ui_type}")
                # print(f"This is the attr name {attr.name}")
                if attr.name == 'class':
                    valid_css_classes = VALID_CSS_STYLES.get(ui_type, set())
                    # print(f"These are the valid css {valid_css_classes}")
                    if attr.value not in valid_css_classes:
                        print(f"Invalid CSS class '{attr.value}' for UI type '{ui_type}'")
                        attr.value = None
                        # raise ValueError(f"Invalid CSS class '{attr.value}' for UI type '{ui_type}'")
                return attr
    UI.model_rebuild()  # This is required to enable recursive types

    class Response(BaseModel):
        ui: UI

    improved_prompt = prompt + f"""
    **Requirements:**
      - You must strictly adhere to the following CSS classes: {css_descriptions}.
      - Do not use any inline or internal styling. Only the provided CSS classes are allowed.

    **Important:** All information provided must be accurately reflected and fully included on the webpage. Ensure that no content is omitted or left out.
    """
    completion = await client_async.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a UI generator AI. You are currently tasked with creating a section of an HTML webpage based on user instructions."},
            {"role": "user", "content": improved_prompt}
        ],
        response_format=Response,
        max_tokens= 5000,
        temperature=0
    )

    ui = completion.choices[0].message
    data_dict = json.loads(ui.content)
    ui_response = data_dict.get("ui")
    return ui_response


async def main():
    content = """
    ### Summary of Lecture

    This lecture covers basic linear algebra content. The key topics discussed include fundamental operations in linear algebra, such as vector addition, scalar multiplication, and the concept of equality in linear equations.

    ### Key Concepts

    - **Addition of Numbers**:
    - The lecture introduces the concept of vector addition. For example, given two vectors \\( \\mathbf{u} = (u_1, u_2) \\) and \\( \\mathbf{v} = (v_1, v_2) \\), their sum is calculated as \\( \\mathbf{u} + \\mathbf{v} = (u_1 + v_1, u_2 + v_2) \\).
    
    - **Multiplication**:
    - Scalar multiplication is another key concept covered. For instance, multiplying a vector \\( \\mathbf{v} = (v_1, v_2) \\) by a scalar \\( c \\) yields \\( c\\mathbf{v} = (cv_1, cv_2) \\).
    
    - **Equality**:
    - The lecture also addresses the concept of equality in linear algebra. Two vectors \\( \\mathbf{u} \\) and \\( \\mathbf{v} \\) are equal if and only if \\( u_1 = v_1 \\) and \\( u_2 = v_2 \\).

    These concepts form the foundational elements of understanding more advanced topics in linear algebra.
    """

    prompt = f"""
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Summary of Lecture**: Create a section that provides a concise overview of the lecture's main points. Use appropriate headings and bullet points to make the content easily digestible.
    - Ensure every detail provided is included: Summary:  This lecture covers basic linear algebra content

    2. **Key Concepts**: Highlight the essential concepts covered in the lecture. Clearly define each concept, and where applicable, accompany them with relevant examples or illustrations. Organize the content effectively using HTML elements like lists or tables.
    - Include every piece of information provided: Key Concept:  The key concept is how to add numbers, multiplication, and equality

    Ensure proper formatting of the content and include all content present.

    {content}
    """
    response = await generate_and_return_ui(prompt,"summary_and_key_concepts")
    return response

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)