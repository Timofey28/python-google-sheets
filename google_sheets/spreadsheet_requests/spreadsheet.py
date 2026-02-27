import json
from enum import StrEnum

from pydantic import BaseModel, Field

from .update_sheet_properties import SheetProperties
from .update_cells import RowData
from .dimension import DimensionProperties
from .conditional_format_rule import ConditionalFormatRule
from .general_models import GridRange


class RecalculationInterval(StrEnum):
    ON_CHANGE = 'ON_CHANGE'
    MINUTE = 'MINUTE'
    HOUR = 'HOUR'


class SpreadsheetProperties(BaseModel):
    title: str
    locale: str = 'ru_RU'
    auto_recalc: RecalculationInterval = Field(None, alias='autoRecalc')
    time_zone: str = Field('Europe/Moscow', alias='timeZone')
    iterative_calculation_settings: dict = Field(None, alias='iterativeCalculationSettings')
    spreadsheet_theme: dict = Field(None, alias='spreadsheetTheme')
    import_functions_external_url_access_allowed: bool = Field(None, alias='importFunctionsExternalUrlAccessAllowed')

    # Read-only
    default_format: dict = Field(None, alias='defaultFormat')

    class Config:
        populate_by_name = True


class GridData(BaseModel):
    start_row: int = Field(None, alias='startRow')
    start_column: int = Field(None, alias='startColumn')
    row_data: list[RowData] = Field(None, alias='rowData')
    row_metadata: list[DimensionProperties] = Field(None, alias='rowMetadata')
    column_metadata: list[DimensionProperties] = Field(None, alias='columnMetadata')


class Sheet(BaseModel):
    properties: SheetProperties = None
    data: list[GridData] = None
    merges: list[GridRange] = None
    conditional_formats: list[ConditionalFormatRule] = Field(None, alias='conditionalFormats')
    filter_views: list[dict] = Field(None, alias='filterViews')
    protected_ranges: list[dict] = Field(None, alias='protectedRanges')
    basic_filter: dict = Field(None, alias='basicFilter')
    charts: list[dict] = None
    banded_ranges: list[dict] = Field(None, alias='bandedRanges')
    developer_metadata: list[dict] = Field(None, alias='developerMetadata')
    row_groups: list[dict] = Field(None, alias='rowGroups')
    column_groups: list[dict] = Field(None, alias='columnGroups')
    slicers: list[dict] = None

    class Config:
        populate_by_name = True


class Spreadsheet(BaseModel):
    properties: SpreadsheetProperties = None
    sheets: list[Sheet] = None
    named_ranges: list[dict] = Field(None, alias='namedRanges')
    developer_metadata: list[dict] = Field(None, alias='developerMetadata')
    data_sources: list[dict] = Field(None, alias='dataSources')

    # Read-only
    spreadsheet_id: str = Field(None, alias='spreadsheetId')
    spreadsheet_url: str = Field(None, alias='spreadsheetUrl')
    data_source_schedules: list[dict] = Field(None, alias='dataSourceSchedules')

    class Config:
        populate_by_name = True


class DeleteSheet(BaseModel):
    sheet_id: int = Field(..., serialization_alias='sheetId')

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}


class AddSheet(BaseModel):
    properties: SheetProperties = None

    def dict(self, *args, **kwargs):
        class_name = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        return {class_name: json.loads(super().json(*args, **kwargs, by_alias=True, exclude_none=True))}
