"""
This module contains the models for the following Google Sheets API requests:

- AddConditionalFormatRule
- DeleteConditionalFormatRule
"""

import json
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator, field_validator

from .general_models import ColorStyle, GridRange, SimpleType
from .update_cells import CellFormat


class InterpolationPointType(StrEnum):
    MIN = 'MIN'
    MAX = 'MAX'
    NUMBER = 'NUMBER'
    PERCENT = 'PERCENT'
    PERCENTILE = 'PERCENTILE'


class InterpolationPoint(BaseModel):
    color_style: ColorStyle = Field(..., alias='colorStyle')
    type: InterpolationPointType
    value: SimpleType | None = None  # Required only for types NUMBER, PERCENT and PERCENTILE

    @field_validator('value', mode='before')
    @classmethod
    def coerce_to_str(cls, v: SimpleType | None):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v

    class Config:
        populate_by_name = True


class RelativeDate(StrEnum):
    PAST_YEAR = 'PAST_YEAR'  # One year before today
    PAST_MONTH = 'PAST_MONTH'  # One month before today
    PAST_WEEK = 'PAST_WEEK'  # One week before today
    YESTERDAY = 'YESTERDAY'
    TODAY = 'TODAY'
    TOMORROW = 'TOMORROW'


class ConditionValue(BaseModel):
    """ Union field, exactly one must be set """
    relative_date: RelativeDate | None = Field(None, alias='relativeDate')
    user_entered_value: SimpleType | None = Field(None, alias='userEnteredValue')

    @field_validator('user_entered_value', mode='before')
    @classmethod
    def coerce_to_str(cls, v: SimpleType | None):
        if v is not None and not isinstance(v, str):
            return str(v)
        return v

    class Config:
        populate_by_name = True


class ConditionType(StrEnum):
    NUMBER_GREATER = 'NUMBER_GREATER'  # Requires ONE ConditionValue
    NUMBER_GREATER_THAN_EQ = 'NUMBER_GREATER_THAN_EQ'  # Requires ONE ConditionValue
    NUMBER_LESS = 'NUMBER_LESS'  # Requires ONE ConditionValue
    NUMBER_LESS_THAN_EQ = 'NUMBER_LESS_THAN_EQ'  # Requires ONE ConditionValue
    NUMBER_EQ = 'NUMBER_EQ'  # Requires ONE ConditionValue ...
    NUMBER_NOT_EQ = 'NUMBER_NOT_EQ'  # Requires ONE ConditionValue ...
    NUMBER_BETWEEN = 'NUMBER_BETWEEN'  # Requires TWO ConditionValue
    NUMBER_NOT_BETWEEN = 'NUMBER_NOT_BETWEEN'  # Requires TWO ConditionValue
    TEXT_CONTAINS = 'TEXT_CONTAINS'  # Requires ONE ConditionValue
    TEXT_NOT_CONTAINS = 'TEXT_NOT_CONTAINS'  # Requires ONE ConditionValue
    TEXT_STARTS_WITH = 'TEXT_STARTS_WITH'  # Requires ONE ConditionValue
    TEXT_ENDS_WITH = 'TEXT_ENDS_WITH'  # Requires ONE ConditionValue
    TEXT_EQ = 'TEXT_EQ'  # Requires ONE ConditionValue ...
    TEXT_IS_EMAIL = 'TEXT_IS_EMAIL'  # Requires NO ConditionValue
    TEXT_IS_URL = 'TEXT_IS_URL'  # Requires NO ConditionValue
    DATE_EQ = 'DATE_EQ'  # Requires ONE ConditionValue ...
    DATE_BEFORE = 'DATE_BEFORE'  # Requires ONE ConditionValue (may be a RelativeDate)
    DATE_AFTER = 'DATE_AFTER'  # Requires ONE ConditionValue (may be a RelativeDate)
    DATE_ON_OR_BEFORE = 'DATE_ON_OR_BEFORE'  # Requires ONE ConditionValue (may be a RelativeDate)
    DATE_ON_OR_AFTER = 'DATE_ON_OR_AFTER'  # Requires ONE ConditionValue (may be a RelativeDate)
    DATE_BETWEEN = 'DATE_BETWEEN'  # Requires TWO ConditionValue
    DATE_NOT_BETWEEN = 'DATE_NOT_BETWEEN'  # Requires TWO ConditionValue
    DATE_IS_VALID = 'DATE_IS_VALID'  # Requires NO ConditionValue
    ONE_OF_RANGE = 'ONE_OF_RANGE'  # Requires ONE ConditionValue
    ONE_OF_LIST = 'ONE_OF_LIST'  # Supports ANY NUMBER of ConditionValue
    BLANK = 'BLANK'  # Requires NO ConditionValue
    NOT_BLANK = 'NOT_BLANK'  # Requires NO ConditionValue
    CUSTOM_FORMULA = 'CUSTOM_FORMULA'  # Requires ONE ConditionValue
    BOOLEAN = 'BOOLEAN'  # Supports ZERO, ONE or TWO ConditionValue
    TEXT_NOT_EQ = 'TEXT_NOT_EQ'  # Requires AT LEAST ONE ConditionValue
    DATE_NOT_EQ = 'DATE_NOT_EQ'  # Requires AT LEAST ONE ConditionValue
    FILTER_EXPRESSION = 'FILTER_EXPRESSION'  # Requires ONE ConditionValue


class BooleanCondition(BaseModel):
    type: ConditionType
    values: list[ConditionValue] = Field(default_factory=list)


class BooleanRule(BaseModel):
    condition: BooleanCondition
    format: CellFormat


class GradientRule(BaseModel):
    minpoint: InterpolationPoint
    midpoint: InterpolationPoint | None = None
    maxpoint: InterpolationPoint


class ConditionalFormatRule(BaseModel):
    ranges: list[GridRange]

    # Union field rule, exactly one must be set
    boolean_rule: BooleanRule | None = Field(None, alias='booleanRule')
    gradient_rule: GradientRule | None = Field(None, alias='gradientRule')

    @model_validator(mode='before')
    @classmethod
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
    rule: ConditionalFormatRule | None = None
    new_index: int | None = Field(None, serialization_alias='newIndex')

    @model_validator(mode='before')
    @classmethod
    def init_before(cls, values: dict):
        if ('rule' in values) == ('new_index' in values):
            raise ValueError('either rule or new_index must be set, but not both')
        return values

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
