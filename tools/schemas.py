from typing import Dict, Any, Type
from pydantic import BaseModel


class BaseToolArgsSchema(BaseModel):
    """Base schema that tool arguments should inherit from."""

    pass


def generate_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Helper to convert a Pydantic model into JSON Schema format."""
    return model.model_json_schema()
