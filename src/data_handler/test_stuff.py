import os
import csv
from .embedded_dataframe import EmbeddingDataFrame
from ..llm_module_generator.llm_base import LLMConfig
from ..credentials import api_key
from .generate_embeddings import GenerateEmbeddings
from .semantic_search import SemanticSearchManager
from .example_based_prompt_formatter import ExampleBasedPromptDataFrame


def main():
    # Set up the base directory and CSV path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'question_embeddings_2024_9_11.csv')
    print(f"CSV Path: {csv_path}")

    # List of questions
    questions = [
    # Linear Algebra / Matrix Algebra
    "I need to generate an online quiz for the following question: Given the system of equations below, solve for the variables \\( x \\), \\( y \\), and \\( z \\) using matrix algebra. \n\\[ \\begin{align*} 2x + 3y - z &= 5 \\\\ x - 4y + 2z &= 3 \\\\ 3x + y + 4z &= 7 \\end{align*} \\]\nWhat HTML elements should I use to allow students to input symbolic values for their solution, ensuring they can submit equations as part of their answer?",

    # Eigenvalues and Eigenvectors (Linear Algebra)
    "I need to generate an online quiz for the following question: Given the matrix: \n\\[ A = \\begin{bmatrix} 4 & 1 \\\\ 2 & 3 \\end{bmatrix} \\]\nFind the eigenvalues and eigenvectors of \\( A \\). What HTML elements should I use to allow students to input their eigenvalue and eigenvector calculations in symbolic form, while also accepting matrix inputs?",

    # Matrix Multiplication (Linear Algebra)
    "I need to generate an online quiz for the following question: Consider the matrices: \n\\[ A = \\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}, \\quad B = \\begin{bmatrix} e & f \\\\ g & h \\end{bmatrix} \\]\nPerform the matrix multiplication \\( A \\times B \\) symbolically and simplify your result. What HTML elements should I use to allow matrix input and symbolic expressions, so students can show their step-by-step solution?",

    # Matrix Inversion (Linear Algebra)
    "I need to generate an online quiz for the following question: Given the 2x2 matrix: \n\\[ M = \\begin{bmatrix} x & y \\\\ z & w \\end{bmatrix} \\]\nFind the inverse of \\( M \\), assuming \\( \\det(M) \\neq 0 \\). What HTML elements should I use to enable students to provide the steps for calculating the inverse of a matrix in symbolic form?",

    # Quadratic Form (Linear Algebra)
    "I need to generate an online quiz for the following question: Given the quadratic form: \n\\[ Q(x, y) = 3x^2 + 4xy + 2y^2 \\]\nExpress \\( Q(x, y) \\) in matrix form \\( x^T A x \\), where \\( x = \\begin{bmatrix} x & y \\end{bmatrix}^T \\) and \\( A \\) is a symmetric matrix. What HTML elements should I use to allow students to input their matrix transformation and verify the symmetric nature of the matrix?",

    # Physics / Mechanics
    "I need to generate an online quiz for the following question: A block of mass \\( m = 5 \\text{kg} \\) is sliding down a frictionless incline of angle \\( 30^\\circ \\). Calculate the acceleration of the block. What HTML elements should I use to allow students to submit symbolic equations and their final answer for the acceleration?",

    # Physics / Mechanics
    "I need to generate an online quiz for the following question: A projectile is launched with an initial velocity of \\( v_0 = 50 \\text{m/s} \\) at an angle of \\( 45^\\circ \\). Find the time of flight and maximum height of the projectile. What HTML elements should I use to enable students to input their symbolic expressions and solutions for both time of flight and height?",

    # Differential Equations
    "I need to generate an online quiz for the following question: Solve the following first-order differential equation: \n\\( \\frac{dy}{dx} + 2y = 5 \\). What HTML elements should I use to allow students to input the general solution of this differential equation, and provide their final answer after applying initial conditions?",

    # Algebra / Polynomial Equations
    "I need to generate an online quiz for the following question: Solve the quadratic equation \\( 2x^2 - 4x + 1 = 0 \\) using the quadratic formula. What HTML elements should I use to enable students to enter symbolic steps and solutions, allowing for complex solutions as well?",

    # Mechanical Engineering / Thermodynamics
    "I need to generate an online quiz for the following question: A piston-cylinder device contains \\( 0.1 \\text{m}^3 \\) of air at \\( 300 \\text{K} \\) and \\( 100 \\text{kPa} \\). The air undergoes an isothermal process until the volume doubles. Calculate the work done by the air. What HTML elements should I use to allow students to input equations involving pressure, volume, and work for thermodynamic calculations?"]


    # Initialize formatter for example-based prompts
    formatter = ExampleBasedPromptDataFrame(
        example_input_column="question",
        example_output_column="question.html",
        api_key=api_key,
        embedding_columns="embeddings-3-small",
        embedding_engine="text-embedding-3-small",
        embedding_file=csv_path
    )

    # List of prompts for formatting
    prompts = [
        "Prompt 1",
        "Prompt 2",
        "Prompt 3",
        "Prompt 4",
        "Prompt 5",
        "Prompt 1",
        "Prompt 2",
        "Prompt 3",
        "Prompt 4",
        "Prompt 5",
    ]

    # Generate and print formatted examples for each question
    for i, question in enumerate(questions):
        examples = formatter.format_examples_prompt(
            template_text=prompts[i],
            query=question,
            threshold=0.5,
            num_examples=1
        )
        print(f"\nPrompt for Question {i + 1}:\n{examples}\n{'='*50}\n")

    # Pretty print extracted examples for the first question
    formatter.pretty_print_extracted_examples(questions[0], threshold=0.5, num_examples=3)


if __name__ == "__main__":
    main()
