from typing import TYPE_CHECKING

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .spreadsheet_requests import Spreadsheet, SheetProperties, RangeData, Dimension, ValueRenderOption, DateTimeRenderOption

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource  # noqa

DEFAULT_PATH_TO_CREDS = 'service_account.json'


class GoogleSheets:
    @staticmethod
    def build_service(path_to_creds: str = DEFAULT_PATH_TO_CREDS) -> 'Resource':
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        try:
            credentials = Credentials.from_service_account_file(path_to_creds, scopes=SCOPES)
        except Exception as e:
            raise e
        return build('sheets', 'v4', credentials=credentials)

    @staticmethod
    def create_spreadsheet(
            title: str,
            folder_id: str = None,
            editing_permissions_for_everyone: bool = False,
            emails: list[str] = None,
            email: str = None,
            path_to_creds: str = DEFAULT_PATH_TO_CREDS,
    ) -> tuple[str, str]:
        """
        Creates a Google Sheet and shares it with the specified emails.

        Args:
            title (str): Table name
            folder_id (str): ID of the folder to place the table in
            editing_permissions_for_everyone (bool): If True, shares the table with everyone who has the link
            emails (list[str]): List of emails to share the table with
            email (str): Single email to share the table with
            path_to_creds (str): Path to the service account credentials JSON file

        Returns:
            tuple[str, str]: ID and URL of the created table respectively
        """
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(path_to_creds, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Create a new Google Sheet
        try:
            file_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.spreadsheet',
            }
            if folder_id:
                file_metadata.update({'parents': [folder_id]})
            spreadsheet_id = drive_service.files().create(body=file_metadata, fields='id').execute()["id"]
        except HttpError as e:
            raise e

        # Share editing permissions with everyone who has a link or with the specified emails
        try:
            if editing_permissions_for_everyone:
                permission = {
                    'type': 'anyone',
                    'role': 'writer'
                }
                drive_service.permissions().create(fileId=spreadsheet_id, body=permission, sendNotificationEmail=False).execute()
            else:
                if emails is None and email is not None:
                    emails = [email]
                for email in emails:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    drive_service.permissions().create(fileId=spreadsheet_id, body=permission, sendNotificationEmail=False).execute()
        except HttpError as e:
            raise e

        return spreadsheet_id, f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'

    @staticmethod
    def update_spreadsheet(spreadsheet_id: str, api_requests: list[dict], *, service: 'Resource') -> None:
        """
        Updates Google Sheet with the specified API requests.

        Args:
            spreadsheet_id (str): ID of the table
            api_requests (list[dict]): List of API requests to update the table
            service (googleapiclient.discovery.Resource): Google Sheets service object
        """
        try:
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': api_requests}).execute(num_retries=5)
        except HttpError as e:
            raise e

    @staticmethod
    def copy_sheet(source_spreadsheet_id: str, source_sheet_id: str, destination_spreadsheet_id: str, *, service: 'Resource') -> SheetProperties:
        request = service.spreadsheets().sheets().copyTo(
            spreadsheetId=source_spreadsheet_id,
            sheetId=source_sheet_id,
            body={'destinationSpreadsheetId': destination_spreadsheet_id}
        )
        try:
            return request.execute(num_retries=5)
        except HttpError as e:
            raise e

    @staticmethod
    def get_spreadsheet(spreadsheet_id: str, service: 'Resource') -> Spreadsheet:
        return Spreadsheet.model_validate(service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute(num_retries=5))

    @staticmethod
    def get_spreadsheet_range_values(
            spreadsheet_id: str,
            sheets: list[str | int] | str | int,
            ranges: list[list[str]] | list[str] | str,
            *,
            by_columns: bool = False,
            service: 'Resource'
    ) -> list[list[RangeData]] | None:
        """
        Reads values from the specified ranges of the table.
        IMPORTANT: If the last cells in the range are empty, they will be omitted. If all cells are empty, an empty
                   list will be returned for that range. However, leading empty cells are preserved and will appear in
                   the result.

        Args:
            spreadsheet_id (str): ID of the table.
            sheets (list[str | int] | str | int): Name or ID of the sheet(s).
            ranges (list[list[str]] | list[str] | str): Single range or list of ranges from each sheet in A1 notation.
            by_columns (bool, optional): If True, returns data organized by columns instead of rows. Defaults to False.
            service (googleapiclient.discovery.Resource): Google Sheets service object.

        Returns:
            list[list[RangeData]] | None: For each range of each sheet, returns a matrix of values (RangeData - list[list[SimpleType]]). Returns None if an error occurs.
        """
        assert \
        (  # sheets: list[str | int], ranges: list[list[str]]
            isinstance(sheets, list) and not isinstance(sheets[0], list) and
            isinstance(ranges, list) and isinstance(ranges[0], list) and not isinstance(ranges[0][0], list) and
            len(sheets) == len(ranges)
        ) or (  # sheets: str | int, ranges: list[str] | str
            isinstance(sheets, (str, int)) and
            (isinstance(ranges, list) and not isinstance(ranges[0], list) or isinstance(ranges, str))
        ), 'sheets and ranges must be either list[str | int] and list[list[str]] respectively and same size, or str | int and list[str] | str respectively'

        # Normalize sheets and ranges to list[str | int] and list[list[str]] respectively
        if isinstance(ranges, str):
            ranges = [ranges]
        if isinstance(sheets, str) or isinstance(sheets, int):
            sheets = [sheets]
            ranges = [ranges]

        ranges_processed = []
        ss = None
        if any(isinstance(sheet, int) for sheet in sheets):
            ss = GoogleSheets.get_spreadsheet(spreadsheet_id, service)
        for sheet_id_or_name, sheet_ranges in zip(sheets, ranges):
            if isinstance(sheet_id_or_name, int):
                try:
                    sheet_name = next(sht.properties.title for sht in ss.sheets if sht.properties.sheet_id == sheet_id_or_name)
                except StopIteration:
                    return None
            else:
                sheet_name = sheet_id_or_name
            ranges_processed.extend([f'{sheet_name}!{range_}' for range_ in sheet_ranges])

        try:
            response = service.spreadsheets().values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=ranges_processed,
                majorDimension=Dimension.COLUMNS if by_columns else Dimension.ROWS,
                valueRenderOption=ValueRenderOption.UNFORMATTED_VALUE,
                dateTimeRenderOption=DateTimeRenderOption.FORMATTED_STRING
            ).execute(num_retries=5)
        except HttpError:
            return None
        else:
            result = []
            value_ranges = iter(response.get('valueRanges', []))
            for sheet_no in range(len(ranges)):
                sheet_ranges = []
                for range_no in range(len(ranges[sheet_no])):
                    sheet_ranges.append(next(value_ranges).get('values', []))
                result.append(sheet_ranges)
            return result
