conceptual_question_ui_prompt = """
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Conceptual Questions**: Create a section dedicated to multiple-choice conceptual questions based on the lecture material. Each question should be clearly presented, with four possible answer choices labeled (A), (B), (C), and (D). Indicate the correct answer for each question.
    - Ensure that all questions and answer choices are formatted using appropriate HTML tags to enhance readability.
    - If any mathematical notation is required within the questions or answer choices, use LaTeX to format it properly.
    """
derivation_ui_prompt = """
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Derivations**: Present any mathematical derivations or logical arguments discussed in the lecture. This section should be meticulously formatted to showcase each step clearly, allowing readers to follow the derivation process step by step. Utilize appropriate HTML tags for mathematical notation and consider using ordered lists or numbered headings to denote each step.
    - Ensure that all derivations are presented in full detail:
    """
summary_ui_prompt = f"""
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.
    """