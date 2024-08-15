import re
def double_curly_brackets(text):
    text = re.sub(r"{", "{{",text)
    text = re.sub(r"}", "}}",text)
    return text
def extract_code_block(text, language):
    pattern = re.compile(rf'```{language}\n(.*?)\n```', re.DOTALL)
    matches = pattern.findall(text)
    return matches[0]
def extract_triple_quotes(text:str)->str:
    pattern = re.compile(r'```.*?\n(.*?)\n```', re.DOTALL)
    matches = pattern.findall(text)
    for match in matches:
        if match:
            return match
        
    
