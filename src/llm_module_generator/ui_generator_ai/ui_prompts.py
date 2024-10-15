conceptual_question_ui_prompt = """
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate. Focus on creating a dedicated section for conceptual multiple-choice questions, ensuring that each question is easy to read and interact with. Use LaTeX to format any mathematical symbols or equations as needed.

    **Instructions:**

    1. **Conceptual Questions**:
       - Each question should have an appropriate, descriptive name that clearly summarizes the topic or concept being tested (e.g., "Newton's Third Law").
       - Present each question in a clear and structured format with four possible answer choices labeled (A), (B), (C), and (D).
       - Use proper HTML tags to ensure readability, such as `<h1>` for the question title, `<h2>` for the question text, and an unordered list (`<ul>`) for the answer choices.
       - Clearly indicate the correct answer for each question, either by adding a note or by using a specific class or tag.
       - If any mathematical notation is required within the question or answer choices, use LaTeX formatting.

    **Example Format** (for reference only, do not include this in your output):
    ```html
    <div class="single-concepetual-question-container">
        <h1>Newton's Third Law</h1>
        <h2>What happens when two objects interact according to Newton's third law?</h2>
        <ul>
          <li>(A) One object exerts a force and the other does not.</li>
          <li>(B) Both objects exert equal and opposite forces on each other.</li>
          <li>(C) The object with greater mass exerts more force.</li>
          <li>(D) Forces are only exerted if the objects are in contact.</li>
        </ul>
        <p><strong>Correct Answer:</strong> (B) Both objects exert equal and opposite forces on each other.</p>
    </div>
    ```

    2. **Mathematical Formatting**:
       - For any mathematical symbols or equations, make sure to use LaTeX enclosed within appropriate delimiters:
         - For block-level equations, use `$$ equation $$` for proper formatting.
         - For inline equations, use `$ equation $` within the body of the text.
       - Ensure that the math is well-spaced and readable, avoiding cluttered or overly dense layouts.

    **General Guidelines**:
       - Ensure proper spacing between questions for readability.
       - Maintain consistent formatting throughout the conceptual questions section.
       - Use appropriate CSS classes to style the elements and enhance the visual appeal.

    **Important:**
    - Do not include headers like "Conceptual Questions" in your response. Focus only on the new question provided.
    - Example of what **not** to do:
    ```html
    <h1>Conceptual Questions</h1>
    <div class="single-concepetual-question-container">
        <h1>Newton's Third Law</h1>
    </div>
    ```
    - Valid response:
    ```html
    <div class="single-concepetual-question-container">
        <h1>Newton's Third Law</h1>
        <h2>What happens when two objects interact according to Newton's third law?</h2>
    </div>
    ```
    """

derivation_ui_prompt = """
    You are a web developer tasked with creating an engaging, well-structured, and informative HTML webpage based on the following extracted lecture notes. The webpage should prioritize clarity, ease of navigation, and visual appeal, with a focus on presenting mathematical derivations.

    **Goal:**
    The purpose of the webpage is to clearly showcase mathematical derivations and logical arguments from the lecture in a way that is easy to read, well-organized, and aesthetically pleasing. Pay particular attention to the presentation of the derivation steps and ensure that all mathematical symbols or equations are properly formatted using LaTeX.

    **Instructions:**

    1. **Derivations**:
       - For each derivation, generate a **descriptive name** that summarizes the key concept or mathematical principle being derived.
       - Present the derivation or logical argument in full, broken down into clear, understandable steps:
         - **Use Ordered Lists** to display the step-by-step process, ensuring that each step is easy to follow.
         - Provide a concise **explanation** for each step using HTML `<p>` tags for descriptions.
         - Format all mathematical expressions using **LaTeX**, enclosed within `$$` for block-level equations and `\\(\\)` for inline equations, to ensure proper rendering.
         - Apply appropriate **CSS classes** to enhance the readability of both the textual explanations and mathematical expressions.
       - Include **metadata** such as whether the derivation requires an image, any additional recommendations, and the source of the derivation.

    2. **Mathematical Formatting:**
       - For any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters:
         - For block-level equations, use `$$ equation $$` for proper formatting.
         - For inline equations, use `$ equation $` within the body of the text.
       - Ensure that the math is well-spaced and readable, avoiding cluttered or overly dense layouts.
       - Ensure proper LaTeX formatting to fix any issues and make sure the mathematical content is displayed correctly.
       - Fix any latext issues you may encounter

    **Example Format (for reference only, do not include this example in the final output):**

    ```html
    <div class="derivation-container">
    <h1>Derivation of the Ideal Gas Law</h1>

    <h2>Step-by-Step Derivation</h2>

    <ol>
      <li>
        <p><strong>Step 1: Start with the basic form of the Ideal Gas Law</strong></p>
        <p>The Ideal Gas Law is given by the equation:</p>
        <p>$$ PV = nRT $$</p>
        <p>Where:</p>
        <ul>
          <li><strong>P</strong> is the pressure</li>
          <li><strong>V</strong> is the volume</li>
          <li><strong>n</strong> is the number of moles</li>
          <li><strong>R</strong> is the gas constant</li>
          <li><strong>T</strong> is the temperature</li>
        </ul>
      </li>

      <li>
        <p><strong>Step 2: Rearrange the equation for pressure</strong></p>
        <p>To solve for pressure, rearrange the equation as follows:</p>
        <p>$$ P = \\frac{{nRT}}{V} $$</p>
      </li>

      <li>
        <p><strong>Step 3: Discuss the assumptions</strong></p>
        <p>This derivation assumes that the gas behaves ideally, meaning that the gas molecules do not interact with each other and occupy negligible volume.</p>
      </li>

      <li>
        <p><strong>Step 4: Final result</strong></p>
        <p>The final result gives us the pressure of an ideal gas in terms of the volume, temperature, and number of moles:</p>
        <p>$$ P = \\frac{nRT}{V} $$</p>
      </li>
    </ol>

    <h2>Metadata</h2>
    <ul>
      <li><strong>Requires Image:</strong> No</li>
      <li><strong>Recommended Resources:</strong> Physics textbook, Thermodynamics chapter</li>
      <li><strong>Source:</strong> Lecture notes on Thermodynamics</li>
    </ul>
    </div>
    ```

    **Key Notes:**
    - This example is meant to serve as a reference for how to structure the derivation content. You should focus only on the specific derivation provided and format it similarly, without including this example in your final output.
    - Ensure the content is easy to navigate by using intuitive heading structures and adequate spacing between derivation steps.
    - Make sure all LaTeX symbols are properly displayed and rendered in the correct mathematical format.

    **Focus on:**
    - Providing clear, concise explanations for each step.
    - Ensuring proper formatting of mathematical symbols and equations.
    - Applying appropriate CSS styling for readability and presentation.
"""




summary_ui_prompt = f"""
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate. Focus on the specific sections outlined below, and ensure proper formatting for mathematical symbols or equations using LaTeX.

    **Summary Section:**
        - Use a `div` container for the summary content.
        - Present key points in bullet form using unordered lists (`ul`) where applicable, or in paragraphs if the content is more narrative.
        - Ensure the summary highlights the most critical information from the lecture, providing readers with a concise overview.

    **Key Concepts Section:**
        - Use a `div` container for the Key Concepts content.
        - Present key concepts in bullet form using unordered lists (`ul`), or in paragraphs for more detailed explanations.
        - Ensure key concepts are clearly structured and easy to identify.
        - Key concepts terms should be bolded
        - Foundational concept terms should be bolded as well

    **Mathematical Formatting:**
       - For any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters:
           - For block-level equations, use `$$ equation $$` for proper formatting.
           - For inline equations, use `$ equation $` within the body of the text.
       - Ensure that the mathematical content is well-spaced and easy to read, avoiding overly dense or cluttered layouts.

    **Example Format:**

    ```html
    <div class="summary-container">
        <h1>Summary of the Lecture</h1>
        <p>This lecture covers the fundamental principles of thermodynamics, including the first and second laws, and the concept of entropy.</p>
        <ul>
            <li>The first law of thermodynamics relates to the conservation of energy.</li>
            <li>The second law introduces the concept of entropy and the directionality of processes.</li>
        </ul>
    </div>

    <div class="key-concepts-container">
        <h2>Key Concepts</h2>
        <ul>
            <li><strong>Conservation of Energy:</strong> Energy cannot be created or destroyed, only transferred or converted.</li>
            <li><strong>Entropy:</strong> A measure of disorder in a system; the second law of thermodynamics states that entropy always increases in an isolated system.</li>
        </ul>
    </div>
    ```

    **General Guidelines:**
       - Use the `span` element to appropriately highlight and bold important information, ensuring it stands out to the reader.
       - Maintain consistent formatting throughout the webpage to ensure clarity and a professional appearance.
    """
