from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


SimpleType = str | int | float | bool


class ThemeColorType(StrEnum):
    TEXT = 'TEXT'
    BACKGROUND = 'BACKGROUND'
    ACCENT1 = 'ACCENT1'
    ACCENT2 = 'ACCENT2'
    ACCENT3 = 'ACCENT3'
    ACCENT4 = 'ACCENT4'
    ACCENT5 = 'ACCENT5'
    ACCENT6 = 'ACCENT6'
    LINK = 'LINK'


class Color(BaseModel):
    red: float = Field(1, ge=0, le=1)
    green: float = Field(1, ge=0, le=1)
    blue: float = Field(1, ge=0, le=1)
    alpha: float = Field(1, ge=0, le=1)


class ColorStyle(BaseModel):
    rgb_color: Color = Field(..., alias='rgbColor')
    theme_color: ThemeColorType = Field(None, alias='themeColor')

    class Config:
        populate_by_name = True


class GridRange(BaseModel):
    """
    A range on a sheet. All indexes are zero-based. Indexes are half open, i.e. the start index is inclusive and the
    end index is exclusive -- [startIndex, endIndex). Missing indexes indicate the range is unbounded on that side.
    """

    sheet_id: int = Field(None, alias='sheetId', ge=0)
    start_row_index: int = Field(..., alias='startRowIndex', ge=0)
    end_row_index: int = Field(..., alias='endRowIndex', gt=0)
    start_column_index: int = Field(..., alias='startColumnIndex', ge=0)
    end_column_index: int = Field(..., alias='endColumnIndex', gt=0)

    @model_validator(mode='after')
    def check_indexes(self):
        if self.start_row_index >= self.end_row_index:
            raise ValueError(f'start_row_index ({self.start_row_index}) must be less than end_row_index ({self.end_row_index})')
        if self.start_column_index >= self.end_column_index:
            raise ValueError(f'start_column_index ({self.start_column_index}) must be less than end_column_index ({self.end_column_index})')
        return self

    class Config:
        populate_by_name = True


class FieldMask:
    TITLE = 'title'
    PIXEL_SIZE = 'pixelSize'

    class GridProperties:
        ALL = 'gridProperties'
        ROW_COUNT = 'gridProperties.rowCount'
        COLUMN_COUNT = 'gridProperties.columnCount'
        FROZEN_ROW_COUNT = 'gridProperties.frozenRowCount'
        FROZEN_COLUMN_COUNT = 'gridProperties.frozenColumnCount'
        HIDE_GRID_LINES = 'gridProperties.hideGridlines'
        ROW_GROUP_CONTROL_AFTER = 'gridProperties.rowGroupControlAfter'
        COLUMN_GROUP_CONTROL_AFTER = 'gridProperties.columnGroupControlAfter'

    class CellData:
        USER_ENTERED_VALUE = 'userEnteredValue'
        USER_ENTERED_FORMAT = 'userEnteredFormat'

    class Spreadsheet:
        ID = 'spreadsheetId'
        URL = 'spreadsheetUrl'
        PROPERTIES = 'properties'
        SHEETS = 'sheets'
