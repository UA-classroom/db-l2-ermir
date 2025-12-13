from pydantic import BaseModel as PydanticBaseModel
from pydantic.alias_generators import to_camel
from pydantic.config import ConfigDict


class BaseModel(PydanticBaseModel):
    """
    Base model for all application models.

    Features:
    - Automatic snake_case to camelCase conversion for JSON serialization
    - Populates models from arbitrary objects/attributes (useful for model-to-model conversion)
    - Handles datetime serialization automatically (Pydantic v2)
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )