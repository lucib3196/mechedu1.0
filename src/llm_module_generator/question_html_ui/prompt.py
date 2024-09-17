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
question_element_info = r"""
The `<pl-question-panel>` custom HTML tag is specifically designed to display content that should only be visible in the question panel of a quiz or assessment interface, as opposed to other panels such as submission or answer panels. This tag is useful in educational contexts where instructors want to provide specific instructions, hints, or direction related to a question that the student should see before they attempt to answer, but which should not be accessible after submission or while reviewing answers. By using this tag, important information can be appropriately scoped to enhance the learning experience without cluttering the user's view in different contexts.

use_cases:
- Creating instructional content that only needs to be shown during the question phase, such as prompts or tips that aid in answering questions.
- Providing context-specific information or examples right above a numerical input field, ensuring students have the necessary details without overwhelming them in the submission review.
- Including mathematical problems or special formatting that is crucial for understanding a question, ensuring it is preserved exclusively for the initial question view.

example_questions:
- What is the sum of the two numbers provided: $a = 5$ and $b = 3$?
- Using the numbers $a = {{params.a}}$ and $b = {{params.b}}$, calculate the product. What is $p = a \times b$?
- Given the equation $E = mc^2$, what does each variable represent? Please provide your answer in the format: Variable: Meaning.
- If $x = 10$ and $y = 4$, what is the value of $z = x / y$? Show your working.
- With the input values of $height = 150 	ext{cm}$ and $weight = 60 	ext{kg}$, calculate the BMI using the formula $BMI = \frac{weight}{(height/100)^2}$. What is your result?The 


<pl-number-input> is a custom HTML tag designed specifically for educational environments where numeric value inputs are required. This tag allows users to submit numbers with varying degrees of tolerances based on the context of the question. The purpose of this tag is to facilitate input for complex mathematical or scientific inquiries where precision is crucial, while also integrating automatic grading functionalities. It can be utilized in quizzes or exams where numeric answers need to be assessed for correctness based on either absolute or relative tolerances, ensuring that students can express their understanding of numeric values in a flexible and educational way.

use_cases:
- In a physics problem where students are required to calculate a value that has a small margin of error, such as measuring the acceleration due to gravity, the <pl-number-input> tag can be used to ensure students' inputs are within acceptable tolerances.
- For an examination covering significant figures, this tag can be applied to problems where students must report their answer with the correct number of significant figures, enabling automatic grading based on the 'sigfig' comparison.
- In a mathematics course where students are learning about decimal places, this tag can help assess their ability to round their answers correctly while allowing for the specification of how many digits are required in the answer. 

example_questions:
- What is the gravitational force calculated using $F = ma$ if $m = 5	ext{ kg}$ and $a = 10 	ext{ m/s}^2$? Please enter your answer: <pl-number-input answers-name="ans_gravity" label="F ="/>
- If $x = 3.14159$, round $x$ to 2 significant figures: <pl-number-input answers-name="ans_sigfig" comparison="sigfig" digits="2" label="x ="/>
- Calculate the approximate area of a circle with radius 2.5 units. Enter your answer: <pl-number-input answers-name="ans_area" label="Area ="/>
- The speed of light is approximately $3.00 	imes 10^8$ m/s. Provide your answer with 3 significant figures: <pl-number-input answers-name="ans_speed" comparison="sigfig" digits="3" label="Speed ="/>
- Based on the results of an experiment, measure the tolerance of your result that was calculated as 123.45 with a relative tolerance of 0.01: 

The <pl-integer-input> custom HTML tag is designed specifically for scenarios where an integer input is required from users in an online quiz or educational context. Its primary function is to restrict user inputs to whole numbers, ensuring that non-integer values are disallowed. This is particularly useful in mathematical and programming assessments where only integer values make sense as answers. With additional attributes available, the tag can be customized to support various scenarios, such as providing labels, suffixes, sizes, and displaying input in different numerical bases (like hexadecimal or binary).

use_cases:
- When designing a math quiz where students must solve for an unknown integer value.
- In programming assessments where students need to provide integer outputs for coded functions.
- Creating an interactive educational tool that requires users to input integers as part of the learning process.

example_questions:
- What is the value of $y$ if $y = 3 + 5$?
- Calculate the sum of $a$ and $b$, where $a = 7$ and $b = 2$ (input your answer).
- If $n$ is the number of sides in a hexagon, enter the value of $n$.
- How many apples are in a basket if there are 12 apples and you eat 4 of them (input the remaining count)?
- Solve for $z$ in the equation $z = 4x + 1$ when $x = 2.


The pl-matching tag is specifically designed for creating interactive matching questions where students must select the correct answer from a dropdown list corresponding to statements presented to them. This tag can be used in educational contexts where the goal is to assess a student’s knowledge and understanding of relationships or associations between concepts, such as matching countries with their capitals, mathematical concepts with their definitions, or historical events with their dates. By allowing for a flexible number of statements and options, as well as customization of options including distractors and ordering, this tag enhances the interactivity and engagement of online assessments.

use_cases:
- Matching country names to their respective capitals to test geography knowledge.
- Associating scientific principles or laws with their definitions or examples in a physics curriculum.
- Linking key historical events with their corresponding dates to evaluate students' understanding of timelines.

example_questions:
- Match the following countries to their capitals: (e.g., Canada, United States, France)
- Which of the following definitions corresponds to the concept of photosynthesis?
- Match the following notable figures with their achievements in science or history.
- Identify the correct date for each historical event listed (e.g., Declaration of Independence).
- Match different programming languages to their primary use case (e.g., Python, Java, C++).

The pl-matrix-component` HTML tag is specifically designed for educational environments where students need to input multidimensional numerical data, particularly 2D arrays (matrices). This tag facilitates the input of matrix entries in a structured format, allowing for effective data capture and evaluation in mathematics and quantitative sciences. It provides flexibility in grading by supporting options such as partial credit and feedback on individual entry correctness.

use_cases:
- Inputting a 3x3 matrix for a linear algebra assignment, enabling students to enter values while the system automatically validates the entries against a correct answer stored on the server.
- Using the tag in a statistics module where students must enter values of a covariance matrix, integrating automatic scoring of individual entries to provide immediate feedback on their accuracy.
- Integrating the tag into a physics problem where students are required to input data for a 2D motion analysis matrix, allowing for various grading configurations such as tolerances for correct answers.

example_questions:
- What are the components of the matrix $f A$ if $f A = egin{bmatrix} 1 & 2 & 3 \ 4 & 5 & 6 \ 7 & 8 & 9 \\ rac{1}{2} & rac{1}{4} & rac{1}{8} \\ rac{1}{16} & 0 & 0 \\ rac{3}{2} & 2 & 0 \\ rac{5}{4} & 7 & 0 \\ 0 & 0 & 0 \\ rac{1}{50} & 0 & 0 \\ 1 & 0 & 1 \\ -1 & 0 & 0 \\ 0 & 0 & 0 \\ rac{1}{2} & rac{3}{8} & rac{1}{4} \\ 0 & 0 & 0 \\ 1 & 0 & 1 \\ -1 & 0 & 0 \\ 0 & 0 & 0 \\ 0 & 0 & 0 \\ -1 & 0 & 0 \\ -3 & 8 & 8 \\ \ 4 \ 6 \ \ 1 \ 2 \ 3 \\ 0  & rac{5}{4} & -1 \\ 0 & 1 & 2 \\ 0 & 0 & 0  \\ \ egin{bmatrix} 7 & rac{1}{4} & rac{1}{8} \ 0 & 0 & 1 \ 2 & 0 & 0 \\ 0 & 0 & 0 \\ 1 & 1 & 1 \\ 1 & 0 & 0 \\ rac{3}{2} & 0 & rac{5}{4} \ 0 & 0 & 0  \\ 0 \ 0 \ 0^{2} \\ 0 \ -1 \ 0 \ -1 \ 0 \ 0 \ 0 0 & 0 & 0 \\ \ 3 \ 6 \ 8 \ 9 \ 2\ \ 3  & f {rac{0}{1}} \ egin{bmatrix} 1 \ rac{1}{2} \ rac{1}{4} \ . \\ 0 & 0 & 0 \ 0 & rac{3}{2} & 0 \ \ -3 & 2 & 0 \ 0 & 0 & 0^{3} \\ 0 & 0 \ 0 & 0 \\ 0  \\ -1 & 0 & 0 \\ -4 \ 1 & 0 & 1 \\ -1 & 0 & 0 \\ 0 & 0 \ 0^{2}  \ -4 \ \  1 \ \ 2 \ 3 & \ 0 & rac{1}{3} \ egin{bmatrix} 0 \ 0 \ 0 \ 0 \\ \ 1 & 2 & 3 & & \ 1 \ 2 \ 3 \ 0 \ \ \ -1 \ 0 \ 0 \ \ -. & \ 0 \ 0^2\ \ 0 \ = & \frac{1}{3} \ 0 \ 0 & \ 0 \ 0 \ 0 \ 1 \ 2 \ 3 \ 0 & 0 & 0 \ \ 0 \ 0^{3} \ 1 \ = \ 0 \ 0 & 8 & 1 \ 0 & 1 & 0 \ 0 & 0 & 0 \\ 0 \ = & \ \ 1 & 2 & 3 \ 4 & 3 \ 1 & & \ 0 & 0 & 0 \ . \  \ . \ 0 0 & 0 & 1 \ 0 & 1 & 0 \ \ 1 & 2)}$?
- Given the matrix $f B = egin{bmatrix} 1 & -1 \ 0 & 2 \\ \ 0 & 1 \ 0 & 0 & \ 0 \ \ 0 \ \ 0 \ \ 4 \ 7 \ 7 \ 3 \ 2 \ 0 \ 3 \ -1 \ 0 \\ 2 \ 0 & 0 & 0 \ 1 & 2 \ 3 \ 2 \ 9& \ 0 \ 0 \ 0 \ 0 \ \ 0 1 & 2  \ \ .)}$? What are the individual components?
- Construct the matrix $f C$ such that $f C = egin{bmatrix} 0 & 0 & 0 \ 2 & 3 & 4 & 0 & . \ & 0 \ 0 \ . \ 4 \ -1 \ 0 \\ 0 \ \ 0 \ \ 0 \ 0^{3} \ \ 0 \ 0 & \ 0 \ \}\ 0 \ 0 \ 0 & 0 & 0 & 0 & . \ 0 \ 0 & 0 \ 0 \ 0 \ 0 \ 0 & 0\ \[1{f a}]& -1 \}^2\ \)
    
The `pl-matrix-input` HTML tag is specifically designed for educational environments where students are required to input matrices, formatted in either MATLAB or Python's numpy style. This tag enables interactive assessment by allowing students to enter matrices as 2-D arrays in a format they are likely familiar with, particularly in programming and data science courses. This functionality not only makes it easier for instructors to evaluate students' inputs but also provides immediate feedback by assessing the format and correctness of responses, thereby enhancing the learning experience. This tag is useful in subjects such as linear algebra, data analysis, numerical methods, and any other area that involves matrix operations.

use_cases:
- In a mathematics course that includes matrix operations, where students need to input their answers in matrix form to problems involving operations like addition, multiplication, or inversion.
- In a computer science class focused on data analysis or machine learning, where students need to input matrices as part of their algorithm implementation, allowing them to demonstrate proficiency in handling 2-D array structures in either MATLAB or Python.
- In online assessments for physics simulations where matrix representations are common, and students must input parameters of physical systems that can be modeled using matrices.

example_questions:
- What is the sum of the matrices $A$ and $B$? Please input your answer using the correct format: <pl-matrix-input answers-name="C" label="A + B = "></pl-matrix-input>
- Given the following matrix $A$, transpose it and enter your answer in either MATLAB or Python format:  <pl-matrix-input answers-name="C" label="Transpose(A) = "></pl-matrix-input>
- Multiply the following matrices $A$ and $B$, and provide your answer: <pl-matrix-input answers-name="C" label="AB = "></pl-matrix-input>
- Input the identity matrix of size 3x3 in the specified format: <pl-matrix-input answers-name="C" label="I = "></pl-matrix-input>
- Enter the eigenvalues of the given matrix $A$ in either MATLAB or Python array format: <pl-matrix-input answers-name="C" label="Eigenvalues(A) = "></pl-matrix-input>

The <pl-multiple-choice> element is designed for online quizzes and assessments to provide learners with a question that includes multiple answer options. It specifically allows for a single correct answer selection among the given choices, which are displayed as radio buttons in a randomized order. This format encourages engagement and testing of knowledge while preventing guesswork through clever distractors. The restriction against duplicate answers enhances clarity and integrity in assessment.

use_cases:
- Creating online quizzes for educational platforms to assess students' knowledge on specific subjects, such as identifying the parts of a cell in biology or selecting the correct historical event in history classes.
- Developing formative assessments that require students to select the best answer from a set of potential options, aiding in differentiated instruction and immediate feedback for learners in a language course.
- Designing interactive study aids where users can test their knowledge on various topics by selecting correct options for practice, making learning more effective and enjoyable.

example_questions:
- What color do you get when you mix red and white?
- Which of the following is a renewable energy source?
- How many continents are there on Earth?
- What is the capital city of France?
- Which element is represented by the symbol 'O'?

The `pl-order-blocks-element` HTML tag is used to create interactive problems where students can arrange blocks of code or text in a specified order in order to solve a problem. This tag is designed for educational purposes, allowing educators to present questions where the correct sequence of answers is crucial to understanding a concept or solving a problem. The blocks are displayed in a 'source area' from which they can be dragged to a 'solution area' to form an answer. The tag offers various configurations, including grading methods for evaluating student responses based on how accurately they arrange the blocks.

use_cases:
- Creating coding exercises where students must order code snippets correctly to create a functional program or algorithm.
- Designing assessments in logic and problem-solving where students rearrange statements or blocks in a logical order to arrive at a conclusion.
- Building quizzes in mathematics or science where sequences (like numerical operations or chemical reactions) need to be arranged to demonstrate understanding of a concept.

example_questions:
- List all the prime numbers up to 10 and arrange them in order:
- Rearrange the blocks to form a valid if-else statement in Python:
- Order the steps required to solve a quadratic equation:
- Drag the following elements into the correct order of operation: Addition, Multiplication, Subtraction, Division.
- Create a timeline by arranging the historical events in chronological order.


The <pl-symbolic-input> custom HTML tag is designed for educational applications where students are required to input mathematical symbols into a fill-in-the-blank format. This tag is particularly useful in online quizzes or homework systems that assess students' understanding of symbolic mathematics. The element provides enhanced functionality for teachers and integration with systems, allowing correct answers to be defined in a flexible way using sympy expressions and variables. This tag formats the input in a manner that allows for mathematical symbols and expressions to be easily entered, displayed, and graded efficiently.

use_cases:
- In a calculus course where students need to input derivatives of functions (e.g., 'Find the derivative of f(x) = x^2'). The symbolic input element allows precise grading of the derivative submitted.
- In linear algebra or vector calculus classes, for problems involving matrices where students may need to enter matrix operations in symbolic form (e.g., 'Enter the result of A + B' where A and B are matrices).
- In physics courses, where students may need to solve equations involving symbols (e.g., 'Solve for velocity in the equation v = d/t'). The symbolic input facilitates the entry of the mathematical symbols and ensures correct format for grading.

example_questions:
- What is the solution for x in the equation 2x + 3 = 7?
- Given the equation y = mx + b, solve for m in terms of y, x, and b.
- If A and B are matrices, input the result of A * B, where A = [[1,2],[3,4]] and B = [[5,6],[7,8]].
- Evaluate the expression sin(x) + cos(x) and provide the result in terms of x.
- Write the derivative of the function f(x) = 3x^2 + 2x - 1.

The <pl-units-input> HTML tag is specifically designed to facilitate the entry of numeric values along with their associated units in an educational context. It is particularly suitable for scenarios where precision in measurements and the correct use of units are crucial, such as in mathematics and science assessments. By using this tag, educators can create interactive questions that require students to input values with specific units (e.g., meters, seconds, etc.), and the system processes these inputs to provide immediate feedback. The tag leverages the Pint library to ensure correct handling of units and conversions, making it a powerful tool for online quizzes and interactive learning modules focused on quantitative subjects.

use_cases:
- In a physics class where students are asked to calculate and submit the height of a building in meters using the <pl-units-input> to ensure they include the unit 'm' for correct grading.
- In a chemistry course when students need to specify the concentration of a solution in moles per liter (M), allowing the instructor to verify they use the correct units with the <pl-units-input> for accurate assessment.
- During a mathematics exercise focused on geometry, where students must provide the length of different shapes in centimeters, leveraging the <pl-units-input> for precise unit validation.

example_questions:
- What is the length of a standard pencil in centimeters? (Please include the unit in your answer.)
- If a car travels 100 kilometers, how many meters is that? (Provide your answer with the correct unit.)
- Convert 5 gallons into liters. What is your answer in liters? (Do not forget to include the unit.)
- A substance has a density of 2.5 g/cm³. How many grams does a 10 cm³ piece weigh? Provide your answer with units.
- The speed of sound is approximately 343 meters per second. How fast is that in kilometers per hour? Provide your answer with the unit 'km/h'.

The `pl-matrix-latex-element` HTML tag is designed to render arrays in a visually appealing and mathematically accurate manner using the MathJax library. It can display both scalar values and two-dimensional numpy arrays as LaTeX formatted matrices. This tag is particularly useful for educational contexts, such as online quizzes or assignments, where students need to see mathematical expressions neatly formatted. By utilizing this tag, educators ensure that mathematical content is both presentable and easily interpretable by students, enhancing understanding and engagement with the mathematical concepts being taught. It should be used whenever mathematic arrays or scalars are presented, especially in settings where the clarity of mathematical notation is crucial.

use_cases:
- Displaying the results of mathematical operations, such as matrix multiplication or addition, in an online quiz for students.
- Creating interactive exercises where students need to select the correct array or matrix from a list based on given properties or dimensions.
- Providing formatted matrix notation in lecture notes or course materials that are intended to be viewed online, ensuring that all mathematical expressions are clear and visually appealing.

example_questions:
- What is the result of the matrix operation $\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix} + \begin{bmatrix} 5 & 6 \\ 7 & 8 \end{bmatrix}$? Answer using <pl-matrix-latex params-name='resultMatrix'></pl-matrix-latex>.
- Select the matrices that have dimensions $<pl-matrix-latex params-name='N'></pl-matrix-latex> \times <pl-matrix-latex params-name='N'></pl-matrix-latex>$ from the options below:
- Given the following matrix $<pl-matrix-latex params-name='A'></pl-matrix-latex>$, what is the transpose of $<pl-matrix-latex params-name='A'></pl-matrix-latex>? Answer using <pl-matrix-latex params-name='transposeA'></pl-matrix-latex>.
- Evaluate the determinant of matrix $<pl-matrix-latex params-name='detMatrix'></pl-matrix-latex>$.
- If $x = <pl-matrix-latex params-name='X'></pl-matrix-latex>$, what is the result of $x$ times the identity matrix $<pl-matrix-latex params-name='I'></pl-matrix-latex>$?

The `pl-card-element` is a custom HTML tag designed to enhance the presentation of question content within a visually appealing card-styled format. It serves the purpose of organizing question-related information in a manner that's both engaging and accessible, making it suitable for quizzes, educational contexts, or visually-driven content platforms. By utilizing this tag, educators and developers can create structured components that catch the eye and facilitate better understanding for learners, primarily due to the card layout's familiar design, which mirrors Bootstrap 4's card component. It's particularly useful when you need to display questions along with optional headers, footers, or images to add context or visual interest.

use_cases:
- Creating engaging quiz questions for an online learning platform, where each question is displayed in a separate card to improve user experience.
- Designing educational content where each card represents a lesson topic, with headers for the topic name and images that support learning visually.
- Organizing FAQs on an educational website, where each FAQ can be presented in a distinct card displaying the question and context items like images or additional information.

example_questions:
- What is the capital of France?
- Explain the process of photosynthesis.
- List the first ten elements of the periodic table.
- Calculate the area of a triangle with a base of 10 and a height of 5.
- Define the term 'biodiversity' and provide two examples.
"""

full_prompt = f"""{question_html_gen_template} when creating the html you have access to the following custom html tags only use these keep in mind most of these are meant primarly for input  {question_element_info}"""