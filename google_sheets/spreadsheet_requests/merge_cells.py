"""
This module contains the models for the following Google Sheets API requests:

- MergeCells
- UnmergeCells
"""

import json
from enum import StrEnum
from pydantic import BaseModel, Field

from .general_models import GridRange


class MergeType(StrEnum):
    MERGE_ALL = 'MERGE_ALL'
    MERGE_COLUMNS = 'MERGE_COLUMNS'
    MERGE_ROWS = 'MERGE_ROWS'


class MergeCells(BaseModel):
    range: GridRange
    merge_type: MergeType = Field(..., serialization_alias='mergeType')

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class UnmergeCells(BaseModel):
    range: GridRange

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
