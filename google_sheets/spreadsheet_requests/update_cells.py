"""
This module contains models for the following Google Sheets API requests:
- UpdateCells
"""

from __future__ import annotations

import json
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from .general_models import GridRange, ColorStyle


class NumberFormatType(StrEnum):
    TEXT = 'TEXT'
    NUMBER = 'NUMBER'
    PERCENT = 'PERCENT'
    CURRENCY = 'CURRENCY'
    DATE = 'DATE'
    TIME = 'TIME'
    DATE_TIME = 'DATE_TIME'
    SCIENTIFIC = 'SCIENTIFIC'

class NumberFormat(BaseModel):
    type_: NumberFormatType = Field(..., alias='type')
    pattern: str = None


class Style(StrEnum):
    DOTTED = 'DOTTED'
    DASHED = 'DASHED'
    SOLID = THIN = 'SOLID'
    SOLID_MEDIUM = MEDIUM = 'SOLID_MEDIUM'
    SOLID_THICK = THICK = 'SOLID_THICK'
    NONE = 'NONE'
    DOUBLE = 'DOUBLE'

class Border(BaseModel):
    style: Style
    color_style: ColorStyle | None = Field(None, serialization_alias='colorStyle')

class Borders(BaseModel):
    top: Border | None = None
    bottom: Border | None = None
    left: Border | None = None
    right: Border | None = None

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values):
        filled_fields = [key for key, value in values.items() if value is not None]
        if len(filled_fields) == 0:
            raise ValueError('at least one border must be set')
        return values


class Padding(BaseModel):
    top: int | None
    right: int | None
    bottom: int | None
    left: int | None

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values):
        filled_fields = [key for key, value in values.items() if value is not None]
        if len(filled_fields) == 0:
            raise ValueError('at least one padding must be set')
        return values


class HorizontalAlignment(StrEnum):
    LEFT = 'LEFT'
    CENTER = 'CENTER'
    RIGHT = 'RIGHT'

class VerticalAlignment(StrEnum):
    TOP = 'TOP'
    MIDDLE = 'MIDDLE'
    BOTTOM = 'BOTTOM'


class WrapStrategy(StrEnum):
    OVERFLOW_CELL = 'OVERFLOW_CELL'
    # LEGACY_WRAP = 'LEGACY_WRAP'  # Not supported on all platforms
    CLIP = 'CLIP'
    WRAP = 'WRAP'


class TextDirection(StrEnum):
    LEFT_TO_RIGHT = 'LEFT_TO_RIGHT'
    RIGHT_TO_LEFT = 'RIGHT_TO_LEFT'


class Link:
    uri: str = None

class TextFormat(BaseModel):
    foreground_color_style: ColorStyle | None = Field(None, serialization_alias='foregroundColorStyle')
    font_family: str | None = Field(None, serialization_alias='fontFamily')
    font_size: int | None = Field(None, serialization_alias='fontSize')
    bold: bool | None = None
    italic: bool | None = None
    strikethrough: bool | None = None
    underline: bool | None = None
    link: Link | None = None

    class Config:
        arbitrary_types_allowed = True


class HyperlinkDisplayType(StrEnum):
    LINKED = 'LINKED'
    PLAIN_TEXT = 'PLAIN_TEXT'


class TextRotation(BaseModel):
    angle: int | None = Field(None, ge=-90, le=90)  # Angle between the standard orientation and the desired orientation, direction is counterclockwise
    vertical: bool | None = None  # Text reads top to bottom, but the orientation of individual characters is unchanged

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values):
        filled_fields = [key for key, value in values.items() if value is not None]
        if len(filled_fields) != 1:
            raise ValueError(f'only one field must be set, but got {filled_fields}')
        return values


class CellFormat(BaseModel):
    number_format: NumberFormat | None = Field(None, alias='numberFormat')
    background_color_style: ColorStyle | None = Field(None, alias='backgroundColorStyle')
    borders: Borders | None = None
    padding: Padding | None = None
    horizontal_alignment: HorizontalAlignment | None = Field(None, alias='horizontalAlignment')
    vertical_alignment: VerticalAlignment | None = Field(None, alias='verticalAlignment')
    wrap_strategy: WrapStrategy | None = Field(None, alias='wrapStrategy')
    text_direction: TextDirection | None = Field(None, alias='textDirection')
    text_format: TextFormat | None = Field(None, alias='textFormat')
    hyperlink_display_type: HyperlinkDisplayType | None = Field(None, alias='hyperlinkDisplayType')
    text_rotation: TextRotation | None = Field(None, alias='textRotation')

    def __add__(self, other) -> CellFormat:
        number_format = other.number_format or self.number_format
        if other.number_format and self.number_format:
            number_format = NumberFormat(
                type=other.number_format.type_ or self.number_format.type_,
                pattern=other.number_format.pattern or self.number_format.pattern,
            )

        borders = other.borders or self.borders
        if other.borders and self.borders:
            borders = Borders(
                top=other.borders.top or self.borders.top,
                bottom=other.borders.bottom or self.borders.bottom,
                left=other.borders.left or self.borders.left,
                right=other.borders.right or self.borders.right,
            )

        text_format = other.text_format or self.text_format
        if other.text_format and self.text_format:
            text_format = TextFormat(
                foreground_color_style=other.text_format.foreground_color_style or self.text_format.foreground_color_style,
                font_family=other.text_format.font_family or self.text_format.font_family,
                font_size=other.text_format.font_size or self.text_format.font_size,
                bold=other.text_format.bold or self.text_format.bold,
                italic=other.text_format.italic or self.text_format.italic,
                strikethrough=other.text_format.strikethrough or self.text_format.strikethrough,
                underline=other.text_format.underline or self.text_format.underline,
                link=other.text_format.link or self.text_format.link,
            )

        return CellFormat(
            number_format=number_format,
            background_color_style=other.background_color_style or self.background_color_style,
            borders=borders,
            padding=other.padding or self.padding,
            horizontal_alignment=other.horizontal_alignment or self.horizontal_alignment,
            vertical_alignment=other.vertical_alignment or self.vertical_alignment,
            wrap_strategy=other.wrap_strategy or self.wrap_strategy,
            text_direction=other.text_direction or self.text_direction,
            text_format=text_format,
            hyperlink_display_type=other.hyperlink_display_type or self.hyperlink_display_type,
            text_rotation=other.text_rotation or self.text_rotation,
        )

    class Config:
        populate_by_name = True


class ExtendedValue(BaseModel):
    number_value: float | None = Field(None, alias='numberValue')
    string_value: str | None = Field(None, alias='stringValue')
    bool_value: bool | None = Field(None, alias='boolValue')
    formula_value: str | None = Field(None, alias='formulaValue')

    # Read-only
    error_value: dict | None = Field(None, alias='errorValue')

    @model_validator(mode='before')
    @classmethod
    def check_exclusive_fields(cls, values):
        filled_fields = [key for key, value in values.items() if value is not None]
        if len(filled_fields) != 1:
            raise ValueError(f'only one field must be set, but got {filled_fields}')
        return values

    class Config:
        populate_by_name = True


class CellData(BaseModel):
    user_entered_value: ExtendedValue | None = Field(None, alias='userEnteredValue')
    user_entered_format: CellFormat | None = Field(None, alias='userEnteredFormat')
    note: str | None = None
    text_format_runs: list[dict] | None = Field(None, alias='textFormatRuns')
    data_validation: dict | None = Field(None, alias='dataValidation')
    pivot_table: dict | None = Field(None, alias='pivotTable')
    data_source_table: dict | None = Field(None, alias='dataSourceTable')
    data_source_formula: dict | None = Field(None, alias='dataSourceFormula')

    # Read-only
    effective_value: ExtendedValue | None = Field(None, alias='effectiveValue')
    formatted_value: str | None = Field(None, alias='formattedValue')
    effective_format: CellFormat | None = Field(None, alias='effectiveFormat')
    hyperlink: str | None = None
    
    class Config:
        populate_by_name = True


class RowData(BaseModel):
    values: list[CellData]


class UpdateCells(BaseModel):
    range: GridRange
    rows: list[RowData] = []
    fields: str

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
