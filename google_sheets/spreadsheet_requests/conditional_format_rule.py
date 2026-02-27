"""
This module contains the models for the following Google Sheets API requests:

- AddConditionalFormatRule
- DeleteConditionalFormatRule
"""

import json
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .general_models import ColorStyle, GridRange


class InterpolationPointType(StrEnum):
    MIN = 'MIN'
    MAX = 'MAX'
    NUMBER = 'NUMBER'
    PERCENT = 'PERCENT'
    PERCENTILE = 'PERCENTILE'


class InterpolationPoint(BaseModel):
    color_style: ColorStyle = Field(..., alias='colorStyle')
    type: InterpolationPointType
    value: str = None

    class Config:
        populate_by_name = True


class BooleanRule(BaseModel):
    condition: dict
    format: dict


class GradientRule(BaseModel):
    minpoint: InterpolationPoint
    midpoint: InterpolationPoint = None
    maxpoint: InterpolationPoint


class ConditionalFormatRule(BaseModel):
    ranges: list[GridRange]
    boolean_rule: BooleanRule = Field(None, alias='booleanRule')
    gradient_rule: GradientRule = Field(None, alias='gradientRule')

    @model_validator(mode='before')
    def init_before(cls, values: dict):
        bool_rule = values.get('boolean_rule', values.get('booleanRule'))
        grad_rule = values.get('gradient_rule', values.get('gradientRule'))
        if (bool_rule is None) == (grad_rule is None):
            raise ValueError('either boolean_rule or gradient_rule must be set, but not both')
        return values

    class Config:
        populate_by_name = True


class AddConditionalFormatRule(BaseModel):
    rule: ConditionalFormatRule
    index: int = 0

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class DeleteConditionalFormatRule(BaseModel):
    index: int
    sheet_id: int

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class UpdateConditionalFormatRule(BaseModel):
    index: int
    sheet_id: int = Field(..., serialization_alias='sheetId')

    # Union field instruction can be only one of the following:
    rule: ConditionalFormatRule = None
    new_index: int = Field(None, serialization_alias='newIndex')

    @model_validator(mode='before')
    def init_before(cls, values: dict):
        if ('rule' in values) == ('new_index' in values):
            raise ValueError('either rule or new_index must be set, but not both')
        return values

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
