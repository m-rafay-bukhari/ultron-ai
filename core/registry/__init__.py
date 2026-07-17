from typing import Dict, Any, Type

class Registry:
    """A generic class registry for dynamic component lookup."""

    def __init__(self) -> None:
        self._registry: Dict[str, Type[Any]] = {}

    def register(self, name: str, cls: Type[Any]) -> None:
        self._registry[name] = cls

    def get(self, name: str) -> Type[Any]:
        if name not in self._registry:
            raise KeyError(f"Component '{name}' is not registered.")
        return self._registry[name]

    def list_registered(self) -> Dict[str, Type[Any]]:
        return dict(self._registry)
