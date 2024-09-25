question_html_gen_template = """
1. Analyze the Question
Begin by carefully reading the physics question to determine its nature—whether it demands computational solutions or is purely theoretical. 
This initial analysis is critical as it dictates the necessity of incorporating placeholders for numerical values. 
Consider the context and specifics of the question thoroughly to ensure the correct categorization.

2. Identify Parameters for Computation
For questions requiring computational analysis:
Identify all numerical values that could potentially vary or would be essential for calculations. This step is paramount and must be prioritized for computational questions.
Replace these values with placeholders using the format {{params.variable_name}}. Ensure you choose descriptive and unique names for each variable to prevent any confusion and to clearly indicate their roles in the computations.

3. Emphasize Placeholder Implementation
The implementation of placeholders is a key aspect of converting physics questions into interactive HTML files. Whenever you encounter a numerical value in a computational question:

Immediately consider it for conversion into a placeholder. For instance, if the question involves a distance traveled over time, convert specific numerical values like "100 meters" and "5 seconds" into {{params.distance}} and {{params.time}}, respectively.
 Ensure that every numerical parameter in the question is accounted for and represented by a placeholder, which will allow for dynamic interaction when the HTML is used.
4. Analyze the Examples
You are provided with a set of examples showcasing the implementation of similar questions:
Analyze these examples critically and revisit the instructions to understand their approaches and outcomes.
Adapt the best practices from these examples to the question at hand, ensuring that placeholders are effectively used to allow end-users to manipulate the variables and explore different computational results.

Additionally, only include files if you are given  the path to the file directly 
"""
question_html_gen_template_nonadaptive = """
Generate a html file given the following examples
"""
server_js_template_base = """
    Design a robust JavaScript module capable of generating computational problems across various STEM disciplines. This module will ingest an HTML file containing a structured query and output a JavaScript snippet that performs the calculations for the described problem. The JavaScript code must conform to the following outline:
    Additionally, the only JavaScript library you are allowed to import is the mathjs library.
    You do not have access to any external files. If needed, generate a small data structure containing a maximum of five properties, such as tabular data for chemical, material, or fluid properties, to demonstrate that the code works.
    const generate = () => {{
        // 1. Dynamic Parameter Selection:
        // - Thoroughly analyze the HTML or data source to identify an extensive range of categories and units for computation.
        // - Ensure the inclusion of a wide variety of units and values, covering different global measurement systems.
        // - Develop a randomized selection algorithm to fairly choose a category or unit system, ensuring equitable representation.
        // - When applicable, ensure that it alternates between SI and USCS for unit selection.

        // 2. Value Generation:
        // - Produce random values relevant to the problem's context, ensuring they fall within specified ranges.
        // - Define static ranges for value generation to avoid conversion issues later on.
        // - When applicable and given the chance to include both SI and USCS, choose to define static values within a specified range rather than converting them later.
        // - Account for both SI and USCS unit systems when applicable, generating appropriate values for each system.

        **Important Note on Unit Conversion:**
        - Do not convert between SI and USCS unless directly stated in the problem. The code should only apply unit conversions within the specified system. Ensure that each problem instance adheres to this rule to maintain accuracy and consistency
        - Do not convert the values when it is not needed for solution synthesis ie do not convert SI values to USCS and vise versa
        // 3. Solution Synthesis:
        // - Utilize the selected parameters and the generated values to formulate the solution.
        // - Apply any necessary unit conversions.

        return {{
            params: {{
                // Input parameters relevant to the problem's context and the chosen category/unit system.
            // Export all calculated variables used during the calculation before applying any unit conversions. These values should be the original values generated, as these will
            // be used for the HTML integration. Ensure that any converted values are also exported if conversions are performed.
            }},
            correct_answers: {{
                // Calculate the correct answer(s) using the selected parameters and generated values.
            }},
            nDigits: 3,  // Define the number of digits after the decimal place.
            sigfigs: 3   // Define the number of significant figures for the answer.
        }};
    }}

    module.exports = {{
        generate
    }}

    Your mission is to flesh out the generate function within this framework. It should dynamically select parameters and units, apply necessary transformations, spawn values, and deduce a legitimate solution. The function must return an object containing params and correct_answers properties, adhering to the prescribed structure. This alignment ensures seamless integration of the HTML and JavaScript components. Below is a sample illustration:
    ```insert javascriptcode here```
    
    """

server_template_code_guide = """
    Additionally, you have access to both a code guide and a solution guide. The solution guide provides an accurate, step-by-step method for solving the problem, dictating the logical approach. 
    The code guide offers guidance on how to implement this solution in code, including formatting and other relevant considerations.
"""

solution_html_template= """
Objective:
        Develop an HTML module to generate comprehensive solutions and step-by-step guides for STEM problems. Utilize specific HTML tags for structural organization and LaTeX for mathematical equations and symbols.

        HTML Tags and LaTeX Integration:
        - <pl-solution-panel>: Used to encapsulate the entire solution guide.
        - <pl-hint level="1" data-type="text">: Employed for providing hints and detailed step-by-step explanations within the guide.
        - LaTeX Integration: Incorporate LaTeX within the HTML to accurately represent mathematical equations and symbols, enhancing clarity and precision.

        Solution Guide Format:
        1. Problem Statement: 
        - Define the problem's objective clearly within a <pl-solution-panel>.

        2. Known Variables Description: 
        - Use <pl-hint> tags to describe all known variables. Include relevant mathematical expressions or equations formatted in LaTeX.

        3. Equation Setup: 
        - Establish equations or relationships necessary to solve the unknown, utilizing LaTeX for mathematical representations within <pl-hint> tags.

        4. Solution Process: 
        - Detail each step of the solution, employing <pl-hint> tags. Represent all mathematical workings and solutions using LaTeX.

        5. Explanation and Clarification: 
        - Provide thorough explanations and clarifications throughout the guide, using LaTeX within <pl-hint> tags for mathematical justifications.

        6. Educational Goal: 
        - The guide should be structured to assist students in mastering the material, emphasizing a deep understanding of the problem-solving process.

        Task:
        - Develop an HTML module to create solutions and guides for STEM problems based on structured HTML questions.
        - The provided solution guide format is as follows: {solution_guide}.
        - Analyze example HTML questions and create guides that align with the provided format.
        
        delimit the html with ```html```
        
        the following are examples that show its implementation
        """
solution_improvement_prompt = """Given the current HTML module for STEM problem-solving, your task is to enhance it using the provided code as a foundational guide. This code is designed to dynamically generate problem parameters and their correct answers. Your objective is to integrate these elements into the HTML solution guide effectively.
        Your Specific Tasks:
        1. **Review the Current ssolution guide  **: 
        Begin by examining the provided HTML solution guide  {solution_generated}. 
        2. **Integrate Dynamic Content Using Placeholders**: Insert placeholders into the HTML that correspond to the outputs of the code found in the params datastructure. Use placeholders like `{{params.placeholder_value}}` or `{{correct_answers.placeholder_value}}` that align with the variable names and data formats in the code. This ensures the HTML will dynamically display the correct data when the module runs.
         Reference Code for Integration:
         {code_guide}
          Include your revised HTML code below:
        return the generated code
        """

server_py_template_base = """
You have access to Python modules such as `numpy`, `sympy`, and `pandas`, which you may use when necessary.

Your task is to design a robust Python module that generates computational problems across various STEM disciplines. This module will ingest an HTML file containing a structured query and output a Python snippet that performs the required calculations. The Python code must adhere to the following outline:

```python
def generate():
    # 1. Dynamic Parameter Selection:
    # - Thoroughly analyze the HTML or data source to identify relevant categories and units for computation.
    # - Ensure the inclusion of a diverse set of units and values, covering different global measurement systems (SI and USCS).
    # - Implement a randomized selection algorithm that fairly alternates between unit systems (SI and USCS), ensuring balanced representation.
    # - Avoid embedding HTML within the Python code.

    # 2. Value Generation:
    # - Randomly generate values relevant to the problem context, ensuring they fall within specified, realistic ranges.
    # - Define static ranges for value generation to avoid conversion issues.
    # - Ensure that values are generated specifically for either SI or USCS without converting between the two unless explicitly stated in the problem.
    # - When necessary, include static values for both SI and USCS systems.

    # **Note on Unit Conversion:**
    # - Only perform unit conversions if explicitly required by the problem.
    # - If the problem involves unit conversion, ensure that conversions are applied correctly within the specified system. Do not convert SI to USCS or vice versa unless necessary.
    # - Original generated values should be retained for further processing, especially for integration with the HTML side.

    # 3. Solution Synthesis:
    # - Use the selected parameters and generated values to formulate the solution.
    # - If necessary, apply appropriate unit conversions during the solution phase, ensuring consistency with the original values.

    return {
        'params': {
            # The input parameters relevant to the problem's context (categories, units, values).
            # Export all original values generated before applying any unit conversions, ensuring consistency for HTML integration.
            # If any conversions were performed, include the converted values alongside the original ones.
        },
        'correct_answers': {
            # The correct answers to the problem, calculated based on the selected parameters and generated values.
        },
        'nDigits': 3,  # The number of digits after the decimal point for numerical answers.
        'sigfigs': 3   # The number of significant figures to be used in the final answer.
    }

    """


generate_metadata_template = """ You are tasked with analyzing the given question and classifying it by generating the appropriate metadata. Use the following structure to ensure accurate classification:

Title: Provide a suitable title for the question in CamelCase format.
Stem: Offer additional context or subtopic related to the main topic of the question.
Topic: Identify the main subject or topic that the question pertains to.
Tags: Provide an array of relevant keywords or tags associated with the question's content.
Prerequisites: List any necessary prerequisites required to understand or engage with the question.
IsAdaptive: Determine whether the question involves any numerical computation. Return true if it requires numerical computation, and false otherwise.

question: {question}"""
