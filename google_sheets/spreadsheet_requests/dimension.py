"""
This module contains the models for the following Google Sheets API requests:

- InsertDimension
- UpdateDimensionProperties
"""

import json
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class Dimension(StrEnum):
    ROWS = 'ROWS'
    COLUMNS = 'COLUMNS'


class DimensionRange(BaseModel):
    sheet_id: int = Field(..., serialization_alias='sheetId', ge=0)
    dimension: Dimension
    start_index: int = Field(..., serialization_alias='startIndex', ge=0)
    end_index: int = Field(..., serialization_alias='endIndex', gt=0)

    @model_validator(mode='after')
    def check_indexes(self):
        if self.start_index >= self.end_index:
            raise ValueError(f'start_index ({self.start_index}) must be less than end_index ({self.end_index})')
        return self


class DimensionProperties(BaseModel):
    hidden_by_user: bool = Field(None, alias='hiddenByUser')
    pixel_size: int = Field(None, alias='pixelSize')
    developer_metadata: dict = Field(None, alias='developerMetadata')
    data_source_column_reference: dict = Field(None, alias='dataSourceColumnReference')

    # Read-only
    hidden_by_filter: bool = Field(None, alias='hiddenByFilter')

    class Config:
        populate_by_name = True


class InsertDimension(BaseModel):
    range: DimensionRange
    inherit_from_before: bool = Field(..., serialization_alias='inheritFromBefore')

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class UpdateDimensionProperties(BaseModel):
    range: DimensionRange
    properties: DimensionProperties
    fields: str

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class AddDimensionGroup(BaseModel):
    range: DimensionRange

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class DeleteDimensionGroup(BaseModel):
    range: DimensionRange

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
