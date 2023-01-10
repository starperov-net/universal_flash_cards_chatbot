from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class Card(BaseModel):
    """Class for validation data for tables.Card model."""

    id: Optional[UUID]
    user: Optional[UUID] = None
    item_relation: Optional[UUID] = None
    author: Optional[UUID] = None
    last_date: Optional[datetime] = None
    memorization_stage: int = Field(None, ge=0, le=7)
    repetition_level: int = Field(None, ge=0, le=8)

    def to_dict_ignore_none(self) -> dict:
        """Get dict which includes data fields as keys and fields values as dicts values, excludes fields with None."""
        return {key: value for key, value in self.dict().items() if not value is None}
