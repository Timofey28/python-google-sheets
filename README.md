# Google Sheets API Python wrapper

Built for developers who want to interact with Google Sheets API in a little more simple way while maintaining peak efficiency.

### Installation
```bash
pip install python-google-sheets
```

### Usage
```python
from google_sheets import GoogleSheets, ApiRequest, CellFormat, TextFormat, TextRotation, Color_

SPREADSHEET_ID = 'your_spreadsheet_id'
SHEET_ID = 0
service = GoogleSheets.build_service(path_to_creds='your_service_account_creds.json')  # 'service_account.json' is used by default

# Update data
api_requests = [
    ApiRequest.update_cells(SHEET_ID, range_='A1:B2', values=[['Bold', 'Italic'], ['Underlined', 'Rotated']]),
    ApiRequest.update_cells(SHEET_ID, range_='A1:B2', cell_formats=[
        [CellFormat(text_format=TextFormat(bold=True)), CellFormat(text_format=TextFormat(italic=True))],
        [CellFormat(text_format=TextFormat(underline=True)), CellFormat(text_rotation=TextRotation(angle=10))],
    ]),
    ApiRequest.update_cells(SHEET_ID, range_='A4:C4', values=['Row', 'of', 'data']),
    ApiRequest.update_cells(SHEET_ID, range_='B6:B8', values=['Column', 'of', 'data']),
    ApiRequest.update_cells(SHEET_ID, range_='A10:C10', values=['This', 'text', 'is colored'], cell_formats=[
        CellFormat(background_color_style=Color_.Basic.YELLOW),
        CellFormat(background_color_style=Color_.Basic.DARK_ORANGE_2),
        CellFormat(background_color_style=Color_.Basic.PLACE_2_10),
    ])
]
GoogleSheets.update_spreadsheet(SPREADSHEET_ID, api_requests=api_requests, service=service)

# Obtain data
values = GoogleSheets.get_spreadsheet_range_values(SPREADSHEET_ID, sheet=SHEET_ID, ranges=['A1:C10'])
```