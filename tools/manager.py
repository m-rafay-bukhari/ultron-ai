import os
import importlib
import inspect
import logging
import pkgutil
from typing import Dict, Any, Type
from core.interfaces.tool import BaseTool
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolManager:
    """Discovers, registers, and instantiates tools automatically from subdirectories."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def discover_tools(self, package_name: str = "tools") -> None:
        """Autodiscover and register all BaseTool subclasses in subpackages."""
        logger.info(f"Starting automatic tool discovery in package '{package_name}'")
        
        try:
            package = importlib.import_module(package_name)
        except ImportError as e:
            logger.error(f"Failed to import tool package {package_name}: {e}")
            return

        path = package.__path__ if hasattr(package, "__path__") else []
        if not path:
            logger.warning(f"No paths found for package {package_name}")
            return

        # Recursively walk subpackages
        for _, module_name, is_pkg in pkgutil.walk_packages(path, package_name + "."):
            # Skip base modules
            if module_name in {"tools.base", "tools.registry", "tools.manager", "tools.executor", "tools.permissions", "tools.schemas", "tools.exceptions"}:
                continue
                
            try:
                module = importlib.import_module(module_name)
                # Find all classes that inherit from BaseTool (excluding BaseTool itself)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseTool) and obj is not BaseTool and not inspect.isabstract(obj):
                        try:
                            # Instantiate and register the tool
                            # Assumes standard empty/default constructor
                            tool_instance = obj()
                            self.registry.register(tool_instance)
                            logger.info(f"Autodiscovered and registered tool class '{name}' from '{module_name}'")
                        except Exception as e:
                            logger.error(f"Failed to initialize discovered tool class '{name}': {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Error importing module {module_name}: {e}")
