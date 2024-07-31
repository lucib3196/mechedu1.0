import re
import pandas as pd

class ExampleBasedPromptFormatter:
    """
    A class for formatting example-based prompts.
    This class provides functionalities to validate and format examples
    and generate prompts based on a template and a set of examples.
    """

    @staticmethod
    def _validate_input(extracted_examples, template_text):
        if not isinstance(extracted_examples, list):
            raise TypeError("Expected extracted_examples to be a list.")
        if not isinstance(template_text, str):
            raise TypeError("Expected template_text to be a string.")

    @staticmethod
    def _validate_example(example):
        print("This is the examples",example)
        if not isinstance(example, dict):
            raise TypeError(f"Expected each example to be a dictionary, but got {type(example)} instead.")
        if 'input' not in example or 'output' not in example:
            raise ValueError("Each example dictionary should have both 'input' and 'output' keys.")
        if not isinstance(example['input'], str) or not isinstance(example['output'], str):
            raise TypeError("Both 'input' and 'output' should be strings.")

    @staticmethod
    def _format_example_set(example_set):
        formatted_examples = []
        for example in example_set:
            ExampleBasedPromptFormatter._validate_example(example)
            if pd.isna(example['output']):
                example['output'] = "PLACEHOLDER"
            formatted_example = f"input: {ExampleBasedPromptFormatter._escape_curly_brackets(example['input'])}\noutput: {ExampleBasedPromptFormatter._escape_curly_brackets(str(example['output']).strip())}"
            formatted_examples.append(formatted_example)
        return "\n\n".join(formatted_examples)

    @staticmethod
    def _escape_curly_brackets(text):
        return re.sub(r'(?<!\{)\{(?!\{)', '{{', re.sub(r'(?<!\})\}(?!\})', '}}', text))

    @staticmethod
    def _generate_prompt(formatted_example, template_text):
        return [f"{ExampleBasedPromptFormatter._escape_curly_brackets(template_text)}\n{formatted_example}\n"]

    @staticmethod
    def run(examples, template_text):
        ExampleBasedPromptFormatter._validate_input(examples, template_text)
        formatted_examples = ExampleBasedPromptFormatter._format_example_set(examples)
        prompt = ExampleBasedPromptFormatter._generate_prompt(formatted_examples, template_text)
        return prompt[0]