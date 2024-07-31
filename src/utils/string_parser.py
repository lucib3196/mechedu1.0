import re
def double_curly_brackets(text):
    text = re.sub(r"{", "{{",text)
    text = re.sub(r"}", "}}",text)
    return text
def extract_code_block(text, language):
    pattern = re.compile(rf'```{language}\n(.*?)\n```', re.DOTALL)
    matches = pattern.findall(text)
    return matches[0]
def extract_triple_quotes(text):
    pattern = r'(""".*?"""|\'\'\'.*?\'\'\'|```.*?```)'
    matches = re.findall(pattern, text, re.DOTALL)
    extracted_contents = [match[3:-3] for match in matches]
    return extracted_contents