import asyncio
from dataclasses import dataclass, field
from bs4 import BeautifulSoup


from openai import BaseModel
from .ui_response import UI, UIType, get_css_description
from ..llm_base import LLM_Call, LLMConfig
from ...credentials import api_key
from ...logging_config.logging_config import get_logger

logger = get_logger(__name__)
def unescape_backslashes(latex_string):
    return latex_string.replace('\\\\', '\\')
@dataclass
class LLMUIBuilder(LLM_Call):
    """
    LLMUIBuilder is a subclass of LLM_Call designed to generate a user interface (UI)
    using a large language model (LLM). The class allows the construction of a UI
    based on a provided prompt and applies predefined CSS categories to the generated
    UI elements.

    Attributes:
        llm_config (LLMConfig): Configuration for the LLM.
        css_category (str): The category of CSS styles to apply.
        css_description (str): A description of the CSS styles applied, initialized in `__post_init__`.
    """

    llm_config: LLMConfig
    css_category: str
    css_description: str = field(init=False)
    total_tokens: int = field(default=0,init=False)

    def __post_init__(self):
        """Initializes the LLMUIBuilder by retrieving the CSS description for the specified category."""
        super().__post_init__()
        self.css_description = get_css_description(UI, self.css_category)
        logger.info(f"Initialized LLMUIBuilder with CSS category: {self.css_category}")

    def define_response(self, ui_instance: UI) -> UI:
        """
        Rebuilds the UI model and sets the valid CSS classes based on the category.

        Args:
            ui_instance (UI): The UI instance to be configured.

        Returns:
            UI: The updated UI instance with valid CSS classes.
        """
        logger.debug("Rebuilding the UI model...")
        ui_instance.model_rebuild()
        
        logger.debug(f"Setting valid CSS classes based on category: {self.css_category}")
        ui_instance.set_valid_css(self.css_category)
        
        valid_css = ui_instance.get_valid_css()
        logger.info("Valid CSS classes set for each UI type:")
        for ui_type, css_classes in valid_css.items():
            logger.info(f"  {ui_type}: {css_classes}")
        
        logger.debug("Updated UI instance:")
        logger.debug(ui_instance)
        
        return ui_instance
    
    async def generate_ui(self, prompt: str, ui_instance: UI) -> str:
        """
        Generates the UI based on a given prompt and applies the defined CSS styles.

        Args:
            prompt (str): The prompt to generate the UI.
            ui_instance (UI): The UI instance to be configured.

        Returns:
            str: The generated HTML representation of the UI.
        """
        logger.info("Generating UI with given prompt...")
        
        ui_instance = self.define_response(ui_instance)
        
        improved_prompt = prompt + f"""
        **Requirements:**
        - You must strictly adhere to the following CSS classes: {self.css_description}.
        - Do not use any inline or internal styling. Only the provided CSS classes are allowed.
        - You can even combine css classes when seen as appropriate

        **Important:** All information provided must be accurately reflected and fully included on the webpage. Ensure that no content is omitted or left out.
        """
        
        response = await self.acall(improved_prompt, response_format=ui_instance)
        html = self.ui_to_html(ui=response)
        logger.info("UI generation completed.")
        return html
    
    def ui_to_html(self, ui: dict) -> str:
        """
        Converts a UI structure represented as a dictionary into HTML.

        Args:
            ui (dict): The UI structure to be converted.

        Returns:
            str: The HTML representation of the UI.
        """
        html = f"<{ui.get('type')}"
        
        if ui.get('attributes'):
            for attribute in ui.get('attributes'):
                html += f' {attribute.get("name")}="{attribute.get("value")}"'
        
        html += ">"
        
        if ui.get("label"):
            unescaped_label = unescape_backslashes(ui.get("label"))
            html += unescaped_label
        
        for child in ui.get("children",""):
            html += self.ui_to_html(child)
        
        html += f"</{ui.get('type')}>"
        return html
        
    def return_css_class(self) -> str:
        """
        Returns the CSS category and description.

        Returns:
            str: The CSS category and its description.
        """
        logger.debug("Returning CSS class and description.")
        return self.css_category, self.css_description
    def get_css_description(self):
        return 
    
async def main():
    logger.info("Starting main function...")
    
    llm_config = LLMConfig(api_key=api_key, model="gpt-4o-mini", temperature=0)
    
    # Initialize LLMUIBuilder properly
    ui_builder = LLMUIBuilder(llm_config=llm_config, css_category="summary_and_key_concepts")
    
    _, description = ui_builder.return_css_class()
    logger.debug(f"CSS Description: {description}")
    
    # Generate the UI asynchronously
    response = await ui_builder.generate_ui("Generate a lecture on how to add numbers include 5 practice problems where the students can practice provide enough space for students to do their work ", ui_instance=UI)
    logger.info("UI generation result:")
    logger.info(response)
    soup = BeautifulSoup(response, 'html.parser')
    print(soup.prettify())
    
    print(ui_builder.get_total_tokens())

if __name__ == "__main__":
    logger.info("Running the script as the main module...")
    asyncio.run(main())

