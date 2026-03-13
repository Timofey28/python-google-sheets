from decimal import Decimal


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


def col_num_to_letter(col_num: int) -> str:
    """
    Converts a column number to its corresponding letter(s) in Excel/Google Sheets.
    """
    result = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        result = chr(65 + remainder) + result
    return result


def col_letter_to_num(col_letter: str) -> int:
    """
    Converts a column letter(s) to its corresponding number in Excel/Google Sheets.
    """
    return sum((ord(c) - 64) * 26**i for i, c in enumerate(col_letter[::-1]))


def rowcol_to_a1(row: int, col: int) -> str:
    """
    Converts row and column numbers to A1 notation.
    """
    col_letter = ""
    while col:
        col, remainder = divmod(col - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
    return f"{col_letter}{row}"


def a1_to_rowcol(a1: str) -> tuple[int, int]:
    """
    Converts a cell in A1 notation to row and column numbers.
    """
    row = int("".join(filter(str.isdigit, a1)))
    col = 0
    for c in a1:
        if c.isalpha():
            col = col * 26 + ord(c) - 64
    return row, col


def float_sum(*floats: float) -> float:
    """
    Sums a variable number of float arguments with high precision using the Decimal class.
    """
    return float(sum(Decimal(str(f)) for f in floats))