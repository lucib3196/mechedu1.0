import os
import sys
import importlib.util
import types

# Initialize logger
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)


def load_module_from_path(module_name: str, file_path: str):
    """
    Dynamically loads a module from the specified file path and handles dependencies by 
    adding the package root to sys.path if not already present.
    
    Args:
        module_name (str): The name to assign to the loaded module.
        file_path (str): The full file path to the module.
    
    Returns:
        Module: The loaded module object.
    """
    # Get the root directory of the file (two levels up from the file path)
    package_root = os.path.abspath(os.path.join(os.path.dirname(file_path), '..', '..',".."))

    # Add package root to sys.path if not already present
    if package_root not in sys.path:
        sys.path.insert(0, package_root)

    # Create a module spec from the file path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load the module from {file_path}")

    # Create a module from the spec
    module = importlib.util.module_from_spec(spec)

    # Execute the module to load it
    spec.loader.exec_module(module) # type: ignore

    # Optionally, add the module to sys.modules to make it available globally
    sys.modules[module_name] = module
    
    return module

def load_controllers(element_info: dict[str, dict], elements_to_call: set[str]) -> dict[str, object]:
    """
    Loads the controller modules for the specified elements by dynamically loading the 
    modules based on the information provided in `element_info`.

    Args:
        element_info (dict[str, dict]): A dictionary containing element information, including paths and controllers.
        elements_to_call (set[str]): A set of element names to load their corresponding controllers.

    Returns:
        dict[str, object]: A dictionary mapping element names to their loaded controller modules.

    Logs:
        - Logs an info message when a module is successfully loaded.
        - Logs an error message if there is an issue loading a module.
    """
    controllers = {}

    for call in elements_to_call:
        try:
            info = element_info.get(call, {})
            controller = info.get("controller", "")  # type: ignore
            root = info.get("path", "")  # type: ignore

            if controller:
                module = load_module_from_path(os.path.basename(root), os.path.join(root, controller))
                controllers[call] = module
                logger.info(f"Module {call} loaded successfully.")
            else:
                logger.warning(f"No controller found for element {call}.")

        except Exception as e:
            logger.error(f"Failed to load module for element {call}: {e}")
    
    return controllers

def run_controller(module: types.ModuleType, function_name: str, *args, **kwargs):
    """
    Executes a function from the given module if it exists and is callable.

    :param module: The module containing the function.
    :param function_name: The name of the function to execute.
    :param *args: Positional arguments to pass to the function.
    :param **kwargs: Keyword arguments to pass to the function.
    :return: The result of the function execution, or None if the function doesn't exist or an error occurs.
    """
    try:
        # Check if the function exists in the module
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            
            # Check if the function is callable
            if callable(func):
                return func(*args, **kwargs)
            else:
                raise TypeError(f"{function_name} is not callable.")
        else:
            raise AttributeError(f"Function {function_name} not found in the module.{module}")
    
    except Exception as e:
        print(f"Error: {e}")
        return None