
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
"""

server_js_template_base = """
    Design a robust JavaScript module capable of generating computational problems across various STEM disciplines. This module will ingest an HTML file containing a structured query and will output a JavaScript snippet that performs the calculations for the described problem. The JavaScript code must conform to the following outline:

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

generate_metadata_template = """
Given the following input question, generate the following metadata
  question: {question}
    - uuid: A universally unique identifier (UUID) for this item
        - title: The title or name of the educational content. Return using CamelCase convention
        - stem: Additional context or a subtopic related to the main topic
        - topic: The main topic or subject of the educational content
        - tags: An array of keywords or tags associated with the content for categorization
        - prereqs: Prerequisites needed to access or understand the content
        - isAdaptive: Designates whether the content necessitates any form of numerical computation. Assign as 'true' if the question involves any numerical computation; return 'false' if no computational effort is required. Note: This is a string value, not a boolean.
        Refer to the predefined list of tags: {tags}. If a tag from this list matches the question's requirements, use it. If the existing tag do not adequately cover the specific needs of the question, you are encouraged to define and introduce a new tag. 
        Consider that multiple concepts—either from the list or newly created—can be relevant and should be included. Each tag should be specific and directly related to mechanical engineering."
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
        ```insert revised html code here```
        """


extract_question_image_template = """Extract only the question being asked from the image. Ensure that it includes all details, data, and parameters necessary for understanding the question comprehensively. Represent any special characters, such as math symbols, using LaTeX format. 
If the image contains multiple questions, return them as an ordered list. Do not extract any other information, such as how to solve the problem or any additional context. 
Your sole objective is to extract the original question(s) from the image."""


extract_solution_image_tempate = """
Analyze the provided image to extract and develop a concise solution guide outlining the methodical steps for solving the problem symbolically. The guide should be clear and to the point, without numerical values, and should include relevant conversion factors.
Solution Guide Format:
Problem Statement:
- Define the problem's objective as depicted in the image, clearly outlining its context and goal.
Variables Description:
- Describe all discernible variables from the image. Include relevant mathematical expressions or equations in LaTeX.
Equation Setup:
- Identify and establish equations or relationships shown or implied in the image, using LaTeX for mathematical representations.
Solution Process:
Detail each step of the solution process as inferred from the image, representing all mathematical workings and potential solutions using LaTeX.
Explanation and Clarification:
- Provide thorough explanations and clarifications based on the image's content, using LaTeX for mathematical justifications.
Symbolic Representation:
- The solution guide should not contain any numerical values; focus on representing the solution symbolically.
Generalization for SI and USCS:
- The solution should be generalized for both SI and USCS. Include relevant conversion factors for both systems if known. If the image provides unit conversion factors, include them. If the conversion factor is not known, do not include it.
Note that questions are typically presented in one unit system at a time, and conversions between SI and USCS within a single question are rare unless explicitly stated.
"""

code_guide_template = """
### Code Guide for Dynamic Problem Generation in JavaScript

#### 0. Analyze the Original Question:
- **Given Values and Units**:
  - Carefully identify all the given values in the original question.
  - Note their units and understand their role within the context of the problem.

#### 1. Variable Ranges:
- **Establishing Variable Ranges**:
  - Identify each variable from the problem statement.
  - Suggest reasonable ranges for each variable.
  - Provide equivalent ranges in both SI and USCS units to ensure consistency.
  - Use the original units from the problem as a baseline for these ranges.

**Example**:
  - If the problem involves speed given in km/h, suggest a range in km/h and the equivalent range in mph.
  - If a distance is given in meters, suggest a range in meters and the equivalent range in feet.

#### 2. Edge Cases:
- **Identify Edge Cases**:
  - Consider scenarios where the problem might break or behave unexpectedly.
  - For instance, if the problem involves division, ensure the divisor is never zero.
  - If the problem involves physical constraints (e.g., negative speeds or distances), ensure these are handled properly.

**Example**:
  - If calculating time, ensure time is never negative.
  - For geometrical problems, ensure dimensions always yield a valid shape (e.g., the sum of two sides of a triangle must always be greater than the third side).

#### 3. Solution Analysis:
- **Key Steps and Methods**:
  - Break down the solution into key steps.
  - Identify the logical sequence and calculations involved.
  - Ensure a clear understanding of the formulae and methods used to arrive at the solution.

**Example**:
  - For a problem calculating kinetic energy, note the steps: identify mass and velocity, use the kinetic energy formula \( KE = \frac{1}{2} mv^2 \).

#### 4. Implementation Strategy:
- **Dynamic Parameter Selection**:
  - Develop a strategy for dynamically selecting and generating problem parameters.
  - Use JavaScript to create random values within the predefined ranges.

**Example**:
  - Use `Math.random()` to generate values for variables within the specified range.
  - Convert these values between SI and USCS as needed.

- **Unit Handling**:
  - Structure the code to handle different units.
  - Apply necessary conversions where appropriate.
  - Ensure that calculations remain consistent across unit systems.

**Example**:
  - Define functions for converting between units (e.g., km/h to mph, meters to feet).
  - Use these functions to switch between SI and USCS units seamlessly.

- **Static Value Ranges**:
  - Define static value ranges directly in the desired unit system.
  - Avoid conversion issues by setting ranges appropriately at the start.

**Example**:
  - If a problem deals with distances, define a range for distances in both meters and feet initially.

#### Additional Notes:
- **Avoid Code Generation in This Phase**:
  - Focus on providing a detailed analysis and strategy.
  - The actual JavaScript code will be implemented later based on this guide.

**Example**:
  - Instead of writing the JavaScript code, outline the logic and structure.
  - Ensure the guide is detailed enough for seamless code translation later.

This guide provides a comprehensive analysis and strategy for developing JavaScript code that dynamically generates similar problems. The focus is on understanding the problem context, defining variable ranges, handling edge cases, analyzing solutions, and developing a robust implementation strategy.
"""




"""Unit Conversion Factors:
- If the image provides unit conversion factors, include them.
- Since we aim to create dynamic content in both SI and USCS, include relevant conversion factors for both systems if known. If the conversion factor is not known, do not include it.
- Note that questions are typically presented in one unit system at a time, and conversions between SI and USCS within a single question are rare unless explicitly stated.
- Just like the variable ranges, the unit conversion factors should be equivalent across unit systems to maintain consistency in the context of the question. For example, if the question requires converting km/h to m/s, the equivalent conversion factor will be mph to ft/s.
- Do not include irrelevant unit conversions that are not used in the question. For instance, omit conversions such as km/h to ft/s unless directly stated."""


server_py_template_base = """
    Design a robust Python module capable of generating computational problems across various STEM disciplines. This module will ingest an HTML file containing a structured query and will output a Python snippet that performs the calculations for the described problem. The Python code must conform to the following outline:

    def generate():
        # 1. Dynamic Parameter Selection:
        # Do not include html inside the python code
        # - Thoroughly analyze the HTML or data source to identify an extensive range of categories and units for computation.
        # - Ensure the inclusion of a wide variety of units and values, covering different global measurement systems.
        # - Develop a randomized selection algorithm to fairly choose a category or unit system, ensuring equitable representation.
        # - When applicable, ensure that it alternates between SI and USCS for unit selection.

        # 2. Value Generation:
        # - Produce random values relevant to the problem's context, ensuring they fall within specified ranges.
        # - Define static ranges for value generation to avoid conversion issues later on.
        # - When applicable and given the chance to include both SI and USCS, choose to define static values within a specified range rather than converting them later.
        # - Account for both SI and USCS unit systems when applicable, generating appropriate values for each system.

        **Important Note on Unit Conversion:**
        # - Do not convert between SI and USCS unless directly stated in the problem. The code should only apply unit conversions within the specified system. Ensure that each problem instance adheres to this rule to maintain accuracy and consistency.
        # - Do not convert the values when it is not needed for solution synthesis i.e., do not convert SI values to USCS and vice versa.

        # 3. Solution Synthesis:
        # - Utilize the selected parameters and the generated values to formulate the solution.
        # - Apply any necessary unit conversions.

        return {
            'params': {
                # Input parameters relevant to the problem's context and the chosen category/unit system.
                # Export all calculated variables used during the calculation before applying any unit conversions. These values should be the original values generated, as these will
                # be used for the HTML integration. Ensure that any converted values are also exported if conversions are performed.
            },
            'correct_answers': {
                # Calculate the correct answer(s) using the selected parameters and generated values.
            },
            'nDigits': 3,  # Define the number of digits after the decimal place.
            'sigfigs': 3   # Define the number of significant figures for the answer.
        }

    if __name__ == "__main__":
        # Example usage
        result = generate()
        print(result)

    Your mission is to flesh out the generate function within this framework. It should dynamically select parameters and units, apply necessary transformations, spawn values, and deduce a legitimate solution. The function must return a dictionary containing 'params' and 'correct_answers' keys, adhering to the prescribed structure. This alignment ensures seamless integration of the HTML and Python components. Below is a sample illustration:
    ```insert python code here```
    
    """


assistant_template = """
Role: You are a personal physics tutor with access to solution guides for specific problems. Your goal is to guide students to find the solutions themselves by asking probing questions and gauging their understanding. You also have access to a code interpreter tool to perform necessary computations.

Guidelines:

Check Solution Availability:

Step 1: When a student asks a question, first check if the solution to the problem is available in the solution guides you have access to.
Unavailable Solution: If the solution is not available, inform the student: "I do not have access to the solution to that particular problem. However, I can try my best to help you understand the concepts and work through it. It is always best to review with a professor or attend office hours for further clarification."
Identify the Problem: If the solution is available, do not use it right away. Instead, proceed to identify the problem and the student's current understanding.

Ask Probing Questions: Ask questions that lead the student to discover the steps and concepts needed to solve the problem. Gauge where they are with the material and identify what they are stuck on.

Provide Hints: If the student is struggling, offer hints or partial steps that can help them progress without giving away the complete answer.

Use Code Interpreter: If the solution requires complex computations, guide the student through the process and use the code interpreter tool to verify their calculations or help them understand the computation steps.

Stay Within Scope: Answer only those questions that are directly related to the problems found in the solution guides. If a question is outside the scope, refer to the step on unavailable solutions.

No Final Answers: Do not give the final answer at all during the session. Your role is to guide and facilitate the student's understanding and problem-solving skills.

Example Prompt:

Student's Question: "How do I calculate the gravitational force between two masses?"
Physics Tutor's Response:
Check Availability: "Let me check if I have access to the solution for this problem. [If not available] I do not have access to the solution to that particular problem. However, I can try my best to help you understand the concepts and work through it. It is always best to review with a professor or attend office hours for further clarification."
Identify Problem: "Great question! Let's start by recalling the formula for gravitational force. Do you remember which law or formula relates the masses and the distance between them to the gravitational force?"
Probing Questions: "What constant is used in this formula and what are its units?"
Follow-up Hint: "If you have the masses of the two objects and the distance between them, how do you think you could set up the equation?"
Code Interpreter Usage: "Let's verify your calculation. What values did you get for the masses and distance? Let’s input them into the formula using the code interpreter:
python
Copy code
G = 6.67430e-11  # Gravitational constant
m1 = 5.97e24  # Mass of the Earth in kg
m2 = 7.35e22  # Mass of the Moon in kg
r = 3.84e8  # Distance between Earth and Moon in meters

F = G * m1 * m2 / r**2
F
"Now, what result do you get from this calculation?"
Clarify Doubts: If the student has follow-up questions or needs clarification on any part of the solution, provide additional guiding questions or hints to help them understand better.
"""




extract_question_image_template = """
You are tasked with analyzing the following image. Extract all the questions found in the image and return them as a JSON structure using the following format:
{
    {
      "question": "extracted question",
      "question_number": "the number of the question",
      "requires_image": true/false,
      "question_complete": true/false
    }
}
Ensure that each question includes all necessary details, data, and parameters to understand the question comprehensively. Represent any special characters, such as math symbols, using LaTeX format. If the question is incomplete, mention this in the JSON structure. If the image contains multiple questions, return them as an ordered list. Do not extract any other information, such as how to solve the problem or any additional context. Your sole objective is to extract the original question(s) from the image. IF empty return None"""
