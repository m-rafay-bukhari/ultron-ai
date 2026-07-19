import importlib
import inspect
import logging
import pkgutil
from services.ai.provider import BaseModelProvider
from services.ai.registry import ProviderRegistry

logger = logging.getLogger(__name__)


class ProviderDiscovery:
    """Automates discovering and registering BaseModelProvider subclasses from python packages."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def discover_and_register(self, package_name: str) -> None:
        """Autodiscover and register all BaseModelProvider classes in the target package."""
        logger.info(f"Starting provider discovery in package: '{package_name}'")
        try:
            package = importlib.import_module(package_name)
        except ImportError as e:
            logger.error(f"Failed to import provider package '{package_name}': {e}")
            return

        path = getattr(package, "__path__", [])
        if not path:
            logger.warning(
                f"No paths associated with provider package: '{package_name}'"
            )
            return

        # Walk package submodules recursively
        for _, module_name, _ in pkgutil.walk_packages(path, package_name + "."):
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if class is a subclass of BaseModelProvider (excluding BaseModelProvider itself)
                    if (
                        issubclass(obj, BaseModelProvider)
                        and obj is not BaseModelProvider
                        and not inspect.isabstract(obj)
                    ):
                        # Extract the registered provider name
                        provider_name = getattr(obj, "provider_name", None)
                        if not provider_name:
                            # Fallback: remove 'Provider' suffix and lowercase
                            provider_name = name.lower()
                            if provider_name.endswith("provider"):
                                provider_name = provider_name[:-8]

                        try:
                            self.registry.register(provider_name, obj)
                            logger.info(
                                f"Discovered and registered provider '{provider_name}' "
                                f"from class '{name}' in module '{module_name}'"
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to register discovered provider class '{name}': {e}"
                            )
            except Exception as e:
                logger.error(f"Failed to load or inspect module '{module_name}': {e}")
