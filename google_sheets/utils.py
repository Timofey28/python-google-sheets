from decimal import Decimal


def col_num_to_letter(col_num: int) -> str:
    """Функция конвертации числового обозначения столбца в буквенное"""

    result = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        result = chr(65 + remainder) + result
    return result

col_index_to_letter: callable = col_num_to_letter


def rowcol_to_a1(row: int, col: int) -> str:
    """Функция конвертации числового обозначения ячейки в буквенное"""
    col_letter = ""
    while col:
        col, remainder = divmod(col - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
    return f"{col_letter}{row}"


def float_sum(*floats: float) -> float:
    """Функция сложения чисел с плавающей точкой"""
    return float(sum(Decimal(str(f)) for f in floats))


# def a1_to_rowcol(cell: str) -> tuple[int, int]:
#     """Функция конвертации буквенного обозначения ячейки в числовое"""
#     row = int("".join(filter(str.isdigit, cell)))
#     col = 0
#     for c in cell:
#         if c.isalpha():
#             col = col * 26 + ord(c) - 64
#     return row, col
#
# def col_letter_to_num(col_letter: str) -> int:
#     """Функция конвертации буквенного обозначения столбца в числовое"""
#     return sum((ord(c) - 64) * 26**i for i, c in enumerate(col_letter[::-1]))
