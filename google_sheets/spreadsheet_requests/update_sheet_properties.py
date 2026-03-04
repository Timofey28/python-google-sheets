"""
This module contains the models for the following Google Sheets API requests:

- UpdateSheetProperties
"""

import json
from pydantic import BaseModel, Field

from .general_models import ColorStyle


class GridProperties(BaseModel):
    row_count: int | None = Field(None, alias='rowCount', gt=0)
    column_count: int | None = Field(None, alias='columnCount', gt=0)
    frozen_row_count: int | None = Field(None, alias='frozenRowCount', ge=0)
    frozen_column_count: int | None = Field(None, alias='frozenColumnCount', ge=0)
    hide_grid_lines: bool | None = Field(None, alias='hideGridlines')
    row_group_control_after: bool | None = Field(None, alias='rowGroupControlAfter')
    column_group_control_after: bool | None = Field(None, alias='columnGroupControlAfter')

    class Config:
        populate_by_name = True


class SheetProperties(BaseModel):
    sheet_id: int | None = Field(None, alias='sheetId', ge=0)
    title: str | None = None
    index: int | None = None
    sheet_type: str | None = Field(None, alias='sheetType')  # Defaults to GRID
    grid_properties: GridProperties | None = Field(None, alias='gridProperties')
    hidden: bool | None = None
    tab_color_style: ColorStyle | None = Field(None, alias='tabColorStyle')
    right_to_left: bool | None = Field(None, alias='rightToLeft')
    data_source_sheet_properties: dict | None = Field(None, alias='dataSourceSheetProperties')

    class Config:
        populate_by_name = True


class UpdateSheetProperties(BaseModel):
    properties: SheetProperties
    fields: str

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
