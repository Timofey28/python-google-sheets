from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .spreadsheet_requests import Spreadsheet, SheetProperties

SimpleType = str | int | float | bool

DEFAULT_PATH_TO_CREDS = 'service_account.json'


class GoogleSheets:
    @staticmethod
    def build_service(path_to_creds: str = DEFAULT_PATH_TO_CREDS):
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
    def update_spreadsheet(spreadsheet_id: str, api_requests: list[dict], service=None) -> None:
        """
        Updates Google Sheet with the specified API requests.

        Args:
            spreadsheet_id (str): ID of the table
            api_requests (list[dict]): List of API requests to update the table
            service (googleapiclient.discovery.Resource): Google Sheets service object
        """
        if service is None:
            service = GoogleSheets.build_service()

        try:
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': api_requests}).execute(num_retries=5)
        except HttpError as e:
            raise e

    @staticmethod
    def copy_sheet(source_spreadsheet_id: str, destination_spreadsheet_id: str, source_sheet_id: str = 0, service=None) -> SheetProperties:
        if service is None:
            service = GoogleSheets.build_service()

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
    def get_spreadsheet(spreadsheet_id: str, service=None) -> Spreadsheet:
        if service is None:
            service = GoogleSheets.build_service()

        return Spreadsheet.model_validate(service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute(num_retries=5))

    @staticmethod
    def get_spreadsheet_range_values(spreadsheet_id: str, sheet: str | int, ranges: list[str], service=None) -> list[list[SimpleType] | list[list[SimpleType]]]:
        """
        Reads values from the specified ranges of the table.
        IMPORTANT: If the last cells in the range are empty, they will be omitted. If all cells are empty, an empty
                   list will be returned for that range. However, leading empty cells are preserved and will appear in
                   the result

        Args:
            spreadsheet_id (str): ID of the table
            sheet (str | int): Name or ID of the sheet
            ranges (list[str]): List of ranges to read in A1 notation
            service (googleapiclient.discovery.Resource): Google Sheets service object

        Returns:
            list[list[str]]: List of values from the specified ranges in the same order
        """
        if service is None:
            service = GoogleSheets.build_service()

        if isinstance(sheet, int):
            ss = GoogleSheets.get_spreadsheet(spreadsheet_id, service)
            try:
                sheet_name = next(sht.properties.title for sht in ss.sheets if sht.properties.sheet_id == sheet)
            except StopIteration:
                return []
        else:
             sheet_name = sheet
        ranges = [f'{sheet_name}!{range_}' for range_ in ranges]

        try:
            response = service.spreadsheets().values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=ranges,
                valueRenderOption='UNFORMATTED_VALUE',
                dateTimeRenderOption='FORMATTED_STRING'
            ).execute(num_retries=5)
        except HttpError as e:
            raise e
        else:
            result = []
            for value_range in response['valueRanges']:
                values = value_range.get('values', [])
                if not values:
                    result.append([])
                    continue

                if len(values) == 1:  # If range is a single row
                    result.append(values[0])
                else:
                    if max([len(row) for row in values]) <= 1:  # If range is a single column
                        result.append([(row[0] if row else '') for row in values])
                    else:
                        result.append(values)

            return result

    @staticmethod
    def get_spreadsheet_id_from_url(url: str) -> str:
        """
        Extracts the ID of the spreadsheet from the URL.

        Args:
            url (str): URL of the table

        Returns:
            str: ID of the table
        """
        if '/edit' in url:
            url = url[:url.index('/edit')]
        return url.split('/')[-1]
