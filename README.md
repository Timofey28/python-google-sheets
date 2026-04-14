# python-google-sheets

A lightweight and efficient Python wrapper for the Google Sheets API v4, leveraging `service account` credentials for seamless authentication.

## Features

- **Batch Operations:** Read multiple ranges or write values and formatting in a single `batchUpdate` request to optimize API quotas.
- **Conditional Formatting:** Full support for boolean rules, gradient rules, presets, updating and deleting rules.
- **Rich Styling:** Built-in `ColorStyle` objects for all standard Google Sheets web interface colors.
- **Developer Friendly:** Designed to simplify complex API interactions into intuitive Pythonic calls.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quickstart)
- [GoogleSheets methods](#googlesheets-methods)
- [ApiRequest methods for batchUpdate](#apirequest-methods-for-batchupdate)
  - [Cell updates](#cell-updates)
  - [Conditional formatting](#conditional-formatting)
  - [Sheet-level operations](#sheet-level-operations)
  - [Merge and freeze](#merge-and-freeze)
  - [Rows and columns](#rows-and-columns)
- [Utility helpers](#utility-helpers)
- [Full example: send multiple requests at once](#full-example-send-multiple-requests-at-once)
- [Support & Feedback](#support--feedback)

## Installation

```sh
pip install python-google-sheets
```

## Quickstart

```python
from google_sheets import GoogleSheets

service = GoogleSheets.build_service('service_account.json')
spreadsheet_id = '1abc...'
sheet_id = 0
```

---

## `GoogleSheets` methods

### `build_service(path_to_creds: str = 'service_account.json') -> 'Resource'`
Create an authorized Google Sheets service client.

```python
service = GoogleSheets.build_service('service_account.json')
```

### `create_spreadsheet(title: str, folder_id: str = None, editing_permissions_for_everyone: bool = False, emails: list[str] = None, email: str = None, path_to_creds: str = 'service_account.json') -> tuple[str, str]`
Create a new spreadsheet and optionally share it. `editing_permissions_for_everyone=True` will allow anyone with the link to edit, while `emails` and `email` parameters can be used to share with specific users or groups. You can also specify a `folder_id` to create the spreadsheet in a specific Google Drive folder.

> **Important:** this method may not work with `service accounts` created after May 2024 due to Google's updated security policies.

```python
spreadsheet_id, url = GoogleSheets.create_spreadsheet(
    title='Monthly Sales Report',
    folder_id='1a2b3c4d5e6f7g8h9i0j',
    emails=['analyst@company.com', 'lead@company.com'],
    path_to_creds='service_account.json',
)
```

### `update_spreadsheet(spreadsheet_id: str, api_requests: list[dict], *, service: 'Resource') -> None`
Execute a `batchUpdate` with one or more request objects.

```python
from google_sheets import ApiRequest

requests = [
    ApiRequest.update_cells(sheet_id=0, range_='A1:C1', values=['Product', 'Qty', 'Revenue']),
]
GoogleSheets.update_spreadsheet(spreadsheet_id, requests, service)
```

### `copy_sheet(source_spreadsheet_id: str, source_sheet_id: str, destination_spreadsheet_id: str, *, service: 'Resource') -> SheetProperties`
Copy a sheet from one spreadsheet into another.

```python
GoogleSheets.copy_sheet(
    source_spreadsheet_id='1source...',
    source_sheet_id=0,
    destination_spreadsheet_id='1destination...',
    service=service,
)
```

### `get_spreadsheet(spreadsheet_id: str, service: 'Resource') -> Spreadsheet`
Fetch spreadsheet metadata (sheets, properties, etc.).

```python
spreadsheet = GoogleSheets.get_spreadsheet(spreadsheet_id, service)
print([sheet.properties.title for sheet in spreadsheet.sheets])
```

### `get_spreadsheet_range_values(spreadsheet_id: str, sheets: list[str | int] | str | int, ranges: list[list[str]] | list[str] | str, *, by_columns: bool = False, service: 'Resource') -> list[list[RangeData]] | None:`
Reads values from multiple ranges across multiple sheets. Returns a matrix of values (RangeData - list[list[SimpleType]]) for each range of each sheet. Returns None if an error occurs.

Code from this example returns one range from sheet with id `1601337967` and three ranges from sheet `Summary` (assuming that these sheets exist in the spreadsheet). You can mix and match sheet names and ids as needed.

```python
values = GoogleSheets.get_spreadsheet_range_values(
    spreadsheet_id=SPREADSHEET_ID,
    sheets=[1601337967, 'Summary'],
    ranges=[['A2:C100'], ['A1:E10', 'F1:F10', 'H1']],
    service=service
)
```

Next two examples return the same data (assuming that sheet `Sheet1` exists and has id `0`). With `by_columns=True` the values are grouped by columns instead of rows.
```python
values = GoogleSheets.get_spreadsheet_range_values(
    SPREADSHEET_ID,
    sheets='Sheet1',
    ranges=['A1:E5'],
    by_columns=True,
    service=service
)
```
```python
values = GoogleSheets.get_spreadsheet_range_values(
    SPREADSHEET_ID,
    sheets=0,
    ranges='A1:E5',
    by_columns=True,
    service=service
)
```
---

## `ApiRequest` methods for `batchUpdate`

Each method below returns a request `dict` that you can pass to `GoogleSheets.update_spreadsheet(...)`.

### Cell updates

### `update_cells(sheet_id: int, range_: str, values: list[list[int | float | bool | str]] | list[int | float | bool | str] = None, cell_formats: list[list[CellFormat]] | list[CellFormat] = None) -> dict`
Write values, formats, or both.

```python
from google_sheets import ApiRequest, CellFormat, TextFormat

req = ApiRequest.update_cells(
    sheet_id=0,
    range_='A1:B2',
    values=[['Plan', 120], ['Actual', 135]],
    cell_formats=[
        [CellFormat(text_format=TextFormat(bold=True)), None],
        [CellFormat(text_format=TextFormat(italic=True)), None],
    ],
)
```

---
### Conditional formatting

### `add_boolean_format_rule(sheet_id: int, ranges: list[str], condition_type: ConditionType, *, condition_values: list[ConditionValue] = None, cell_format: CellFormat) -> dict`
Add a rule (for example, highlight values greater than `100`).

```python
from google_sheets import ConditionType, ConditionValue, CellFormat, Color_, TextFormat

req = ApiRequest.add_boolean_format_rule(
    sheet_id=0,
    ranges=['C2:C100'],
    condition_type=ConditionType.NUMBER_GREATER,
    condition_values=[ConditionValue(user_entered_value=100)],
    cell_format=CellFormat(
        background_color_style=Color_.ConditionalFormatting.GREEN,
        text_format=TextFormat(bold=True),
    ),
)
```

### `GradientRule.add(sheet_id: int, *, ranges: list[str], interpolation_points: tuple[IPTypeAndValue, IPTypeAndValue] | tuple[IPTypeAndValue, IPTypeAndValue, IPTypeAndValue], interpolation_point_colors: tuple[ColorStyle, ColorStyle] | tuple[ColorStyle, ColorStyle, ColorStyle]) -> dict`
Add a custom color scale with 2 or 3 interpolation points.

```python
from google_sheets import InterpolationPointType, Color_

req = ApiRequest.GradientRule.add(
    sheet_id=0,
    ranges=['D2:D100'],
    interpolation_points=(
        (InterpolationPointType.MIN, None),
        (InterpolationPointType.NUMBER, 150),
        (InterpolationPointType.MAX, None),
    ),
    interpolation_point_colors=(
        Color_('#2ca958'),
        Color_.Basic.LIGHT_YELLOW_3,
        Color_.ConditionalFormatting.RED,
    )
)
```

### `GradientRule.add_preset(sheet_id: int, ranges: list[str], preset: Preset) -> dict`
Add a gradient rule from a built-in preset.

```python
req = ApiRequest.GradientRule.add_preset(
    sheet_id=0,
    ranges=['E2:E100'],
    preset=ApiRequest.GradientRule.Preset.RED_YELLOW_GREEN_PERCENTILE,
)
```

### `delete_conditional_format_rule(sheet_id: int, *, index: int) -> dict`
Delete a conditional format rule by index.

```python
req = ApiRequest.delete_conditional_format_rule(sheet_id=0, index=0)
```

### `update_conditional_format_rule(sheet_id: int, *, index: int, rule: ConditionalFormatRule) -> dict`
Replace an existing conditional format rule by index.

```python
from google_sheets import GoogleSheets, ApiRequest
from google_sheets import (
    ConditionalFormatRule,
    GradientRule,
    InterpolationPoint,
    InterpolationPointType,
    BooleanRule,
    BooleanCondition,
    ConditionType,
    ConditionValue,
    GridRange,
    CellFormat,
    TextFormat,
    Color_,
)

rule1 = ConditionalFormatRule(
    ranges=[GridRange(sheet_id=0, **ApiRequest._split_excel_range('A1:A1000',return_as_dict=True))],
    boolean_rule=BooleanRule(
        condition=BooleanCondition(
            type=ConditionType.NUMBER_NOT_BETWEEN,
            values=[ConditionValue(user_entered_value=10), ConditionValue(user_entered_value=30)]
        ),
        format=CellFormat(
            background_color_style=Color_.ConditionalFormatting.GREEN,
            text_format=TextFormat(bold=True)
        ),
    )
)
rule2 = ConditionalFormatRule(
    ranges=[GridRange(sheet_id=0, **ApiRequest._split_excel_range('A1:A1000',return_as_dict=True))],
    gradient_rule=GradientRule(
        minpoint=InterpolationPoint(
            color_style=Color_.ConditionalFormatting.GREEN,
            type=InterpolationPointType.MIN,
        ),
        midpoint=InterpolationPoint(
            color_style=Color_.ConditionalFormatting.YELLOW,
            type=InterpolationPointType.PERCENTILE,
            value=50,
        ),
        maxpoint=InterpolationPoint(
            color_style=Color_.ConditionalFormatting.RED,
            type=InterpolationPointType.MAX,
        ),
    )
)

req1 = ApiRequest.update_conditional_format_rule(sheet_id=0, index=0, rule=rule1)
req2 = ApiRequest.update_conditional_format_rule(sheet_id=0, index=1, rule=rule2)

GoogleSheets.update_spreadsheet(SPREADSHEET_ID, api_requests=[req1, req2], service=service)
```

### Sheet-level operations

### `update_sheet_title(sheet_id: int, title: str) -> dict`
Rename a sheet.

```python
req = ApiRequest.update_sheet_title(sheet_id=0, title='June 2026')
```

### `remove_grid(sheet_id: int) -> dict`
Hide grid lines on a sheet.

```python
req = ApiRequest.remove_grid(sheet_id=0)
```

### `set_sheet_size(sheet_id: int, rows: int = None, columns: int = None) -> dict`
Resize a sheet.

```python
req = ApiRequest.set_sheet_size(sheet_id=0, rows=200, columns=12)
```

### `delete_sheet(sheet_id: int) -> dict`
Delete a sheet.

```python
req = ApiRequest.delete_sheet(sheet_id=3)
```

### `add_sheet(sheet_id: int = None, *, title: str = None, index: int = None, hidden: bool = None, row_count: int = None, column_count: int = None, frozen_row_count: int = None, frozen_column_count: int = None, hide_grid_lines: bool = None) -> dict`
Create a new sheet with optional properties.

```python
req = ApiRequest.add_sheet(
    title='Archive',
    row_count=100,
    column_count=8,
    hide_grid_lines=True,
)
```

---
### Merge and freeze

### `merge_cells(sheet_id: int, range_: str, merge_type: MergeType = MergeType.MERGE_ALL) -> dict`
Merge cells in a range.

```python
req = ApiRequest.merge_cells(sheet_id=0, range_='A1:C1')
```

### `unmerge_cells(sheet_id: int, *, range_: str = None, start_row: int = None, end_row: int = None, start_column: int | str = None, end_column: int | str = None) -> dict`
Unmerge cells in a range (or by explicit indexes).

```python
req = ApiRequest.unmerge_cells(sheet_id=0, range_='A1:C1')
```

### `freeze(sheet_id: int, rows: int = 0, columns: int = 0) -> dict`
Freeze top rows and/or left columns.

```python
req = ApiRequest.freeze(sheet_id=0, rows=1, columns=1)
```

---
### Rows and columns

### `insert_rows(sheet_id: int, start_index: int, end_index: int = None, *, inherit_from_before: bool = True) -> dict`
Insert one or more rows (Indexes are zero-based and inclusive [start_index, end_index]).

```python
req = ApiRequest.insert_rows(sheet_id=0, start_index=5, end_index=9)
```

### `insert_columns(sheet_id: int, start_index: int, end_index: int = None, *, inherit_from_before: bool = True) -> dict`
Insert columns (Indexes are zero-based and inclusive [start_index, end_index]).

```python
req = ApiRequest.insert_columns(sheet_id=0, start_index=2, end_index=3)
```

### `delete_rows(sheet_id: int, start_index: int, end_index: int = None) -> dict`
Delete one or more rows (Indexes are zero-based and inclusive [start_index, end_index]).

```python
req = ApiRequest.delete_rows(sheet_id=0, start_index=5, end_index=9)
```

### `delete_columns(sheet_id: int, start_index: int, end_index: int = None) -> dict`
Delete columns (Indexes are zero-based and inclusive [start_index, end_index]).

```python
req = ApiRequest.delete_columns(sheet_id=0, start_index=2, end_index=3)
```

### `clear_columns(sheet_id: int, rows_count: int, start_index: int, end_index: int = None) -> dict`
Clear values and formatting in one or more columns (Indexes are zero-based and inclusive [start_index, end_index]).

```python
req = ApiRequest.clear_columns(sheet_id=0, rows_count=500, start_index=4, end_index=5)
```

### `set_column_width(sheet_id: int, col_no_or_letter: int | str, width: int) -> dict`
Set a specific column width in pixels.

```python
req = ApiRequest.set_column_width(sheet_id=0, col_no_or_letter='B', width=220)
```

### `set_row_height(sheet_id: int, row_no: int, height: int) -> dict`
Set a specific row height in pixels.

```python
req = ApiRequest.set_row_height(sheet_id=0, row_no=1, height=36)
```

### `set_standard_cell_dimensions(sheet_id: int, rows: int, columns: int) -> tuple[dict, dict]`
Apply default row/column dimensions to a full area.

```python
row_req, col_req = ApiRequest.set_standard_cell_dimensions(
    sheet_id=0,
    rows=1000,
    columns=26,
)
```

### `add_dimension_group(sheet_id: int, dimension: Dimension, start_index: int, end_index: int) -> dict`
Create an outline group for rows or columns.

```python
from google_sheets import Dimension

req = ApiRequest.add_dimension_group(
    sheet_id=0,
    dimension=Dimension.ROWS,
    start_index=10,
    end_index=30,
)
```

### `delete_dimension_group(sheet_id: int, dimension: Dimension, start_index: int, end_index: int) -> dict`
Remove an existing outline group.

```python
req = ApiRequest.delete_dimension_group(
    sheet_id=0,
    dimension=Dimension.ROWS,
    start_index=10,
    end_index=30,
)
```

---

## Utility helpers

### `get_spreadsheet_id_from_url(url: str) -> str`
Extract a spreadsheet ID from a full Google Sheets URL.

```python
from google_sheets import get_spreadsheet_id_from_url

spreadsheet_id = get_spreadsheet_id_from_url(
    "https://docs.google.com/spreadsheets/d/1abcDEFghiJKLmnoPQRstuVWXyz/edit?gid=0#gid=0"
)
```

### `col_num_to_letter(col_num: int) -> str`
Convert a 1-based column number to letters.

```python
from google_sheets import col_num_to_letter

print(col_num_to_letter(28))  # AB
```

### `col_letter_to_num(col_letter: str) -> int`
Convert column letters to a 1-based number.

```python
from google_sheets import col_letter_to_num

print(col_letter_to_num('AB'))  # 28
```

### `rowcol_to_a1(row: int, col: int) -> str`
Convert `(row, col)` into A1 notation.

```python
from google_sheets import rowcol_to_a1

print(rowcol_to_a1(7, 3))  # C7
```

### `a1_to_rowcol(a1: str) -> tuple[int, int]`
Convert A1 notation into `(row, col)`.

```python
from google_sheets import a1_to_rowcol

print(a1_to_rowcol('C7'))  # (7, 3)
```

### `float_sum(*floats: float) -> float`
Sum floating-point numbers with high precision using the Decimal class.

```python
from google_sheets import float_sum

print(float_sum(0.1, 0.2, 0.3))  # 0.6
```

---

## Full example: send multiple requests at once

```python
requests = [
    ApiRequest.update_cells(sheet_id=0, range_='A1', values=['KPI']),
    ApiRequest.freeze(sheet_id=0, rows=1),
    ApiRequest.set_column_width(sheet_id=0, col_no_or_letter=1, width=240),
]
GoogleSheets.update_spreadsheet(spreadsheet_id, requests, service)
```

---

## Support & Feedback

If you have any questions, encounter issues, or want to suggest improvements:

- **Bug Reports & Feature Requests:** Please use [GitHub Issues](https://github.com/Timofey28/python-google-sheets/issues) to report bugs or submit ideas.
- **Questions:** For general inquiries or help with integration, feel free to reach out via email at [timegorr@gmail.com](mailto:timegorr@gmail.com).