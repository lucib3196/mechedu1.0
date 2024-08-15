from enum import Enum

class UIType(str,Enum):
        div = "div"
        p = "p"
        ul = "ul"
        ol = "ol"
        li = "li"
        h1 = "h1"
        h2 = "h2"
        h3 = "h3"
        span = "span"
        strong = "strong"

        @classmethod
        def add_element(cls,name:str,value:str):
                if not hasattr(cls,name):
                        new_element = Enum(name,{name:value})
                        cls._member_map_[name] = new_element[name]
                        cls._value2member_map_[value] = new_element[name]
                else:
                    raise ValueError(f"Element {name} already exists in UIType.")
                
if __name__ == "__main__":
       ui = UIType