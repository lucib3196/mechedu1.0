conceptual_question_prompt = """
    You are tasked with analyzing the following lecture slides covering a specific class topic. Please address the following:

    1. **Conceptual Questions**: Generate 4 multiple-choice conceptual questions based on the lecture material, each with 4 options. Indicate the correct answer for each question.
    These questions can either be derived based on the information from the lecture slides or they can be generated by you. If you decide to generate, you need to indicate this in the response as a bool.
    Always return the sources of where these questions are derived from.
    
    Format any mathematical symbols or equations using LaTeX.
    """
lecture_analysis_prompt ="""
    You are tasked with analyzing the following lecture slides covering a specific class topic. Please address the following questions and return the results as a JSON structure with the specified keys:

    1. **summary**: Provide a comprehensive summary of the lecture material.
    2. **key_concepts**: Identify and explain the key concepts presented in the lecture. Provide a summary of each concept and any relevant background information. If the content requires a math equation, use LaTeX to render the equation and delimit using $.
    3. **keywords**: Describe the lecture content using relevant keywords.
    4. **foundational_concepts**: Determine and outline the foundational concepts that the lecture builds upon.
    """
extract_derivations_prompt= """
        You are tasked with analyzing the following lecture slides covering a specific class topic. Please address the following points and return the results as a JSON structure with the specified keys:

        1. **Derivations**: Extract all derivations found in the lecture material. For each derivation:
            - Provide a name that describes what the derivation is trying to show.
            - Extract the full solution, including all steps as if teaching a student. Ensure to use LaTeX to render any mathematical symbols or equations, delimited by $ symbols.
            - Note that similar derivations may exist for different cases. Distinctions are often indicated by differences in images or new derivation contexts. Identify and separate these accurately.
            - Mention the completeness of each derivation. If a derivation appears incomplete, explicitly indicate this.
            - If no derivations are present, return "NaN".
            """
extract_computation_questions_prompt = """
Extract and process the content from the provided image according to these guidelines:

1. **Question Extraction:**
   - Extract all the computational questions from the image or lecture material. Ensure that all necessary details, data, and parameters are included to fully understand the question.
   - Represent any special characters, such as mathematical symbols, in LaTeX format.
   - Clearly identify and extract the source of the question.

2. **Solution Steps:**
   - For each question, provide a detailed solution with step-by-step explanations. Use LaTeX for formatting any mathematical symbols or equations.
   - Ensure that the solution guide strictly adheres to the symbolic representation requirement, with no numerical values included in the steps.

3. **Image Requirements:**
   - Determine if any images are required to fully understand or solve the question.
   - If images are required, provide a description of the necessary images, detailing what they should depict.
   - Extract and list all image requirements associated with the question.

4. **External Data Requirements:**
   - Identify if the question requires any external data, such as tabular data or charts, to be solved.
   - If external data is required, provide a detailed description of the required data and its relevance to the question.
   - Ensure that all external data requirements are clearly stated.

Ensure that all extracted information is complete, accurate, and formatted according to the provided guidelines.
"""