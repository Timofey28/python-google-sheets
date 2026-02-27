import re

from .spreadsheet_requests import (
    # conditional_format_rule
    AddConditionalFormatRule,
    DeleteConditionalFormatRule,
    UpdateConditionalFormatRule,
    ConditionalFormatRule,
    GradientRule,
    InterpolationPoint,
    InterpolationPointType,

    # update_sheet_properties
    UpdateSheetProperties,
    SheetProperties,
    GridProperties,

    # merge_cells
    MergeType,
    MergeCells,
    UnmergeCells,

    # dimension
    InsertDimension,
    UpdateDimensionProperties,
    AddDimensionGroup,
    DeleteDimensionGroup,
    DimensionProperties,
    DimensionRange,
    Dimension,

    # update_cells
    UpdateCells,
    RowData,
    CellData,
    ExtendedValue,
    CellFormat,

    # general_models
    ColorStyle,
    GridRange,
    FieldMask,

    # spreadsheet
    AddSheet,
    DeleteSheet,
)


class ApiRequest:
    @staticmethod
    def update_cells(
            sheet_id: int,
            range_: str,
            values: list[list[int | float | bool | str]] | list[int | float | bool | str] = None,
            cell_formats: list[list[CellFormat]] | list[CellFormat] = None
    ) -> dict:
        assert values or cell_formats, 'At least one of the parameters must be specified: values or cell_formats'
        start_row, end_row, start_col, end_col = ApiRequest.__split_excel_range(range_)

        # syntax sugar for single row or column
        if values and not isinstance(values[0], list):
            if start_row == end_row:
                values = [values]
            elif start_col == end_col:
                values = [[value] for value in values]
        if cell_formats and not isinstance(cell_formats[0], list):
            if start_row == end_row:
                cell_formats = [cell_formats]
            elif start_col == end_col:
                cell_formats = [[cell_format] for cell_format in cell_formats]

        if values is None:
            values = [[None] * len(cell_formats[0]) for _ in cell_formats]
            fields = FieldMask.CellData.USER_ENTERED_FORMAT
        elif cell_formats is None:
            cell_formats = [[None] * len(values[0]) for _ in values]
            fields = FieldMask.CellData.USER_ENTERED_VALUE
        else:  # Both values and cell_formats are specified
            fields = '*'

        return UpdateCells(
            range=GridRange(
                sheet_id=sheet_id,
                start_row_index=start_row - 1,
                end_row_index=end_row,
                start_column_index=start_col - 1,
                end_column_index=end_col
            ),
            rows=[RowData(
                values=[CellData(
                    user_entered_value=ExtendedValue(
                        number_value=value if isinstance(value, (int, float)) and not isinstance(value, bool) else None,
                        bool_value=value if isinstance(value, bool) else None,
                        string_value=value if isinstance(value, str) and not value.startswith('=') else None,
                        formula_value=value if isinstance(value, str) and value.startswith('=') else None
                    ) if value is not None else None,
                    user_entered_format=cell_format
                ) for value, cell_format in zip(values_row, cell_formats_row)]
            ) for values_row, cell_formats_row in zip(values, cell_formats)],
            fields=fields
        ).dict()

    @staticmethod
    def add_conditional_format_rule(
            *,
            sheet_id: int,
            ranges: list[str],
            gradient_colors: tuple[ColorStyle, ColorStyle, ColorStyle] | tuple[ColorStyle, ColorStyle],
            gradient_points: tuple[float, float, float] = None
    ) -> dict:
        grid_ranges = [GridRange(sheet_id=sheet_id, **ApiRequest.__split_excel_range(range_, return_as_dict=True)) for range_ in ranges]
        if gradient_points is None:
            gradient_points = (None,) * len(gradient_colors)
        if len(gradient_colors) == 2:
            return AddConditionalFormatRule(rule=ConditionalFormatRule(
                ranges=grid_ranges,
                gradient_rule=GradientRule(
                    minpoint=InterpolationPoint(
                        color_style=gradient_colors[0],
                        type=InterpolationPointType.MIN,
                        value=str(gradient_points[0])
                    ),
                    maxpoint=InterpolationPoint(
                        color_style=gradient_colors[1],
                        type=InterpolationPointType.MAX,
                        value=str(gradient_points[1])
                    )
                )
            )).dict()
        return AddConditionalFormatRule(rule=ConditionalFormatRule(
            ranges=grid_ranges,
            gradient_rule=GradientRule(
                minpoint=InterpolationPoint(
                    color_style=gradient_colors[0],
                    type=InterpolationPointType.NUMBER,
                    value=str(gradient_points[0])
                ),
                midpoint=InterpolationPoint(
                    color_style=gradient_colors[1],
                    type=InterpolationPointType.NUMBER,
                    value=str(gradient_points[1])
                ),
                maxpoint=InterpolationPoint(
                    color_style=gradient_colors[2],
                    type=InterpolationPointType.NUMBER,
                    value=str(gradient_points[2])
                )
            )
        )).dict()

    @staticmethod
    def delete_conditional_format_rule(*, sheet_id: int, index: int) -> dict:
        return DeleteConditionalFormatRule(sheet_id=sheet_id, index=index).dict()

    @staticmethod
    def update_conditional_format_rule(*, sheet_id: int, index: int, rule: ConditionalFormatRule) -> dict:
        return UpdateConditionalFormatRule(sheet_id=sheet_id, index=index, rule=rule).dict()

    @staticmethod
    def update_sheet_title(sheet_id: int, title: str) -> dict:
        return UpdateSheetProperties(
            properties=SheetProperties(
                sheet_id=sheet_id,
                title=title
            ),
            fields=FieldMask.TITLE
        ).dict()

    @staticmethod
    def remove_grid(sheet_id: int) -> dict:
        return UpdateSheetProperties(
            properties=SheetProperties(
                sheet_id=sheet_id,
                grid_properties=GridProperties(hide_grid_lines=True)
            ),
            fields=FieldMask.GridProperties.HIDE_GRID_LINES
        ).dict()

    @staticmethod
    def set_sheet_size(sheet_id: int, rows: int = None, columns: int = None) -> dict:
        assert rows is not None or columns is not None, 'At least one of the parameters must be specified: rows or columns'
        if rows and columns:
            fields = f'{FieldMask.GridProperties.ROW_COUNT},{FieldMask.GridProperties.COLUMN_COUNT}'
        elif rows:
            fields = FieldMask.GridProperties.ROW_COUNT
        else:
            fields = FieldMask.GridProperties.COLUMN_COUNT

        return UpdateSheetProperties(
            properties=SheetProperties(
                sheet_id=sheet_id,
                grid_properties=GridProperties(
                    row_count=rows,
                    column_count=columns
                )
            ),
            fields=fields
        ).dict()

    @staticmethod
    def merge_cells(sheet_id: int, range_: str, merge_type: MergeType = MergeType.MERGE_ALL) -> dict:
        start_row, end_row, start_col, end_col = ApiRequest.__split_excel_range(range_)
        return MergeCells(
            range=GridRange(
                sheet_id=sheet_id,
                start_row_index=start_row - 1,
                end_row_index=end_row,
                start_column_index=start_col - 1,
                end_column_index=end_col
            ),
            merge_type=merge_type
        ).dict()

    @staticmethod
    def unmerge_cells(
            sheet_id: int,
            range_: str = None,
            start_row: int = None,
            end_row: int = None,
            start_column: int | str = None,
            end_column: int | str = None,
    ) -> dict:
        assert range_ or (start_row and end_row and start_column and end_column), 'Either range_ or start_row, end_row, start_column, end_column must be specified'
        if range_:  # range_ has priority
            start_row, end_row, start_column, end_column = ApiRequest.__split_excel_range(range_)
        else:
            start_column = ApiRequest.__get_column_index(start_column) if isinstance(start_column, str) else start_column
            end_column = ApiRequest.__get_column_index(end_column) if isinstance(end_column, str) else end_column
        return UnmergeCells(
            range=GridRange(
                sheet_id=sheet_id,
                start_row_index=start_row - 1,
                end_row_index=end_row,
                start_column_index=start_column - 1,
                end_column_index=end_column
            )
        ).dict()

    @staticmethod
    def freeze(sheet_id: int, rows: int = 0, columns: int = 0) -> dict:
        return UpdateSheetProperties(
            properties=SheetProperties(
                sheet_id=sheet_id,
                grid_properties=GridProperties(
                    frozen_row_count=rows,
                    frozen_column_count=columns
                )
            ),
            fields=f'{FieldMask.GridProperties.FROZEN_ROW_COUNT},{FieldMask.GridProperties.FROZEN_COLUMN_COUNT}'
        ).dict()

    @staticmethod
    def insert_rows(sheet_id: int, start_index: int, end_index: int = None, inherit_from_before: bool = True) -> dict:
        """
        Indexes are zero-based and inclusive [start_index, end_index]. If end_index is not specified, then a single
        row will be inserted at start_index.
        """
        end_index = end_index or start_index
        return InsertDimension(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.ROWS,
                start_index=start_index,
                end_index=end_index + 1
            ),
            inherit_from_before=inherit_from_before
        ).dict()

    @staticmethod
    def insert_columns(sheet_id: int, start_index: int, end_index: int = None, inherit_from_before: bool = True) -> dict:
        """
        Indexes are zero-based and inclusive [start_index, end_index]. If end_index is not specified, then a single
        column will be inserted at start_index.
        """
        end_index = end_index or start_index
        return InsertDimension(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.COLUMNS,
                start_index=start_index,
                end_index=end_index + 1
            ),
            inherit_from_before=inherit_from_before
        ).dict()

    @staticmethod
    def clear_columns(sheet_id: int, rows_count: int, start_index: int, end_index: int = None) -> dict:
        """
        Delete data and formatting in columns. Indexes are zero-based and inclusive [start_index, end_index].
        """
        end_index = end_index or start_index
        return UpdateCells(
            range=GridRange(
                sheet_id=sheet_id,
                start_row_index=0,
                end_row_index=rows_count,
                start_column_index=start_index,
                end_column_index=end_index + 1
            ),
            fields='*'
        ).dict()

    @staticmethod
    def set_column_width(sheet_id: int, col_no_or_letter: int | str, width: int) -> dict:
        if isinstance(col_no_or_letter, str):
            col_no = ApiRequest.__get_column_index(col_no_or_letter)
        else:
            col_no = col_no_or_letter
        return UpdateDimensionProperties(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.COLUMNS,
                start_index=col_no - 1,
                end_index=col_no
            ),
            properties=DimensionProperties(
                pixel_size=width
            ),
            fields=FieldMask.PIXEL_SIZE
        ).dict()

    @staticmethod
    def set_row_height(sheet_id: int, row_no: int, height: int) -> dict:
        return UpdateDimensionProperties(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.ROWS,
                start_index=row_no - 1,
                end_index=row_no
            ),
            properties=DimensionProperties(
                pixel_size=height
            ),
            fields=FieldMask.PIXEL_SIZE
        ).dict()

    @staticmethod
    def set_standard_cell_dimensions(sheet_id: int, rows: int, columns: int) -> tuple[dict, dict]:
        return UpdateDimensionProperties(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.ROWS,
                start_index=0,
                end_index=rows
            ),
            properties=DimensionProperties(pixel_size=21),
            fields=FieldMask.PIXEL_SIZE
        ).dict(), UpdateDimensionProperties(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.COLUMNS,
                start_index=0,
                end_index=columns
            ),
            properties=DimensionProperties(pixel_size=100),
            fields=FieldMask.PIXEL_SIZE
        ).dict()

    @staticmethod
    def add_dimension_group(sheet_id: int, dimension: Dimension, start_index: int, end_index: int) -> dict:
        """
        Indexes are zero-based and inclusive [start_index, end_index].
        """
        return AddDimensionGroup(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=dimension,
                start_index=start_index,
                end_index=end_index + 1
            )
        ).dict()

    @staticmethod
    def delete_dimension_group(sheet_id: int, dimension: Dimension, start_index: int, end_index: int) -> dict:
        """
        Indexes are zero-based and inclusive [start_index, end_index].
        """
        return DeleteDimensionGroup(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=dimension,
                start_index=start_index,
                end_index=end_index + 1
            )
        ).dict()

    @staticmethod
    def delete_sheet(sheet_id: int) -> dict:
        return DeleteSheet(sheet_id=sheet_id).dict()

    @staticmethod
    def add_sheet(
            *,
            sheet_id: int = None,
            title: str = None,
            index: int = None,
            hidden: bool = None,
            row_count: int = None,
            column_count: int = None,
            frozen_row_count: int = None,
            frozen_column_count: int = None,
            hide_grid_lines: bool = None,
    ) -> dict:
        return AddSheet(properties=SheetProperties(
            sheet_id=sheet_id,
            title=title,
            index=index,
            hidden=hidden,
            grid_properties=GridProperties(
                row_count=row_count,
                column_count=column_count,
                frozen_row_count=frozen_row_count,
                frozen_column_count=frozen_column_count,
                hide_grid_lines=hide_grid_lines
            )
        )).dict()

    @staticmethod
    def __split_excel_range(range_: str, return_as_dict: bool = False) -> tuple[int, int, int, int] | dict[str, int]:
        if ':' in range_:
            match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)$", range_)
            if not match:
                raise ValueError(f'Unsupported range format: {range_}')
            start_column, start_row, end_column, end_row = match.groups()

        else:
            match = re.match(r"([A-Z]+)(\d+)$", range_)
            if not match:
                raise ValueError(f'Unsupported range format: {range_}')
            start_column, start_row = match.groups()
            end_column, end_row = start_column, start_row

        start_row, end_row = int(start_row), int(end_row)
        start_column, end_column = ApiRequest.__get_column_index(start_column), ApiRequest.__get_column_index(end_column)
        if start_row > end_row or start_column > end_column:
            raise ValueError(f'Invalid range: {range_}')

        if return_as_dict:
            return {
                'start_row_index': start_row - 1,
                'end_row_index': end_row,
                'start_column_index': start_column - 1,
                'end_column_index': end_column
            }
        return start_row, end_row, start_column, end_column

    @staticmethod
    def __get_column_index(column_letters: str) -> int:
        column_index = 0
        for i, letter in enumerate(column_letters[::-1].upper()):
            column_index += (ord(letter) - 64) * (26 ** i)
        return column_index
