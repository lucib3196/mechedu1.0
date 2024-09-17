from bs4 import BeautifulSoup,Tag
from dataclasses import dataclass,field
import bs4
from typing import Optional,Dict


from ..logging_config.logging_config import get_logger
logger = get_logger(__name__)
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional, Dict
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class TagReplacer:
    html: str
    target_tag: str
    replacement_tag: str
    attributes: Optional[Dict[str, str]] = field(default_factory=dict)
    mapping: Optional[Dict[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        self.soup = BeautifulSoup(self.html, "html.parser")

    def replace_tag(self) -> BeautifulSoup:
        target_tags = self.soup.find_all(self.target_tag)

        for target in target_tags:
            logger.info(f"Here is the target tag contents {target.contents} with type {type(target.contents)}")
            old_attributes = target.attrs
            mapped_attributes = self.map_attributes(old_attributes=old_attributes, mapping=self.mapping)
            self.attributes.update(mapped_attributes)

            new_tag = self.soup.new_tag(self.replacement_tag, **self.attributes)
            for child in target.contents:
                logger.info(f"Here is the child {child}")
                new_tag.append(child)
                logger.info(f"Here is the new tag with the child {new_tag}")
            target.replace_with(new_tag)

            logger.info(f"Replaced '{self.target_tag}' with '{self.replacement_tag}' and attributes: {self.attributes}")

        return self.soup

    def replace_tag_unique(self) -> BeautifulSoup:
        target_tag = self.soup.find(self.target_tag)
        
        if target_tag:
            old_attributes = target_tag.attrs
            mapped_attributes = self.map_attributes(old_attributes=old_attributes, mapping=self.mapping)
            self.attributes.update(mapped_attributes)

            new_tag = self.soup.new_tag(self.replacement_tag, **self.attributes)
            for child in list(target_tag.children):
                new_tag.append(child.extract())

            target_tag.replace_with(new_tag)

            logger.info(f"Replaced first '{self.target_tag}' with '{self.replacement_tag}' and attributes: {self.attributes}")
        
        logger.debug(self.soup.prettify())
        return self.soup
    def auto_replace(self)->BeautifulSoup:
        try:
            target_tags = self.soup.find_all(self.target_tag)
            print(f"This is the target tag: {target_tags}, This is the length: {len(target_tags)}")
            
            if len(target_tags) == 1:
                return self.replace_tag_unique()
            elif len(target_tags) > 1:
                return self.replace_tag()
            else:
                logger.warning(f"No tags found for {self.target_tag}")
                return self.soup

        except Exception as e:
            logger.exception(f"Could not resolve {self.target_tag}: {e}")
            return None
    def map_attributes(self, old_attributes: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, str]:
        new_attributes = {}
        
        # Map attributes based on the provided mapping
        for old_key, new_key in mapping.items():
            if old_key in old_attributes:
                new_attributes[new_key] = old_attributes[old_key]
                logger.info(f"Mapping '{old_key}' to '{new_key}' with value '{old_attributes[old_key]}'")
        
        # Check if all attributes were mapped
        unmapped_keys = set(old_attributes.keys()) - set(mapping.keys())
        if unmapped_keys:
            logger.warning(f"Did not map all the values. Unmapped attributes: {unmapped_keys}")
        
        return new_attributes
    def update_soup(self,html:str):
        self.soup =  BeautifulSoup(html, "html.parser")

def main():
    html_string = r"""
    <pl-question-panel>
      <pl-figure file-name="gas_laws.png"></pl-figure>
    <p>The figure above illustrates concepts related to gases under certain conditions. Which of the following is the ideal gas law equation?
    </p>
    </pl-question-panel>
    <pl-checkbox answers-name="idealGas" weight="1" inline="true">
      <pl-answer correct="true">\( PV = nRT \)</pl-answer>
      <pl-answer correct="false">\( P = \rho RT \)</pl-answer>
      <pl-answer correct="false">\( P = \frac{m}{V} \)</pl-answer>
      <pl-answer correct="false">\( P = \frac{RT}{m} \)</pl-answer>
    </pl-checkbox>
    """
    # First replacement: <pl-question-panel> to <div>
    pl_panel_replacer = TagReplacer(
        html=html_string,
        target_tag="pl-question-panel",
        replacement_tag="div",
        attributes={"class": "question-panel-wrapper"}
    )
    new_soup = pl_panel_replacer.auto_replace()
    print("After replacing <pl-question-panel> with <div>:\n", new_soup.prettify())

    # Second replacement: <pl-answer> to <input type="checkbox">
    mapping = {"correct": "data-correct"}
    pl_answer_replacer = TagReplacer(
        html=str(new_soup),
        target_tag="pl-answer",
        replacement_tag="input",
        attributes={"type": "checkbox"},
        mapping=mapping
    )
    new_soup = pl_answer_replacer.auto_replace()
    print("After replacing <pl-answer> with <input type='checkbox'>:\n", new_soup.prettify())

    # Third Replacement <pl-checkbox>
    mapping = {
        "answers-name": "answers-name",
        "weight": "data-weight",
        "inline": "data-inline"
    }
    pl_checkbox_replacer = TagReplacer(
        html=str(new_soup),
        target_tag="pl-checkbox",
        replacement_tag="fieldset",
        attributes={"class": "checkbox-group"},
        mapping=mapping
    )
    new_soup = pl_checkbox_replacer.auto_replace()
    print(new_soup.prettify())


if __name__ == "__main__":
    main()


