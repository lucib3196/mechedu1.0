from .generate_ui import generate_and_return_ui
import asyncio



def unescape_backslashes(latex_string):
    return latex_string.replace('\\\\', '\\')
def ui_to_html(ui: dict) -> str:
    # Start with the opening tag
    html = f"<{ui.get('type')}"

    # Add attributes
    if ui.get('attributes'):
        for attribute in ui.get('attributes'):
            html += f' {attribute.get("name")}="{attribute.get("value")}"'


    # Close the opening tag
    html += ">"

    #Add the label if it exists
    if ui.get("label"):
        unescaped_label = unescape_backslashes(ui.get("label"))
        # print(unescaped_label, "\n")
        html += unescaped_label
        # print(unescaped_label)

    # Recursively add children
    for child in ui.get("children"):
        html += ui_to_html(child)

    # Add the closing tag
    html += f"</{ui.get('type')}>"

    return html


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
    ui_to_html(response)
    return ui_to_html(response)

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)