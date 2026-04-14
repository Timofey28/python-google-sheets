import re
from enum import StrEnum

from .styles import Color_
from .spreadsheet_requests import (
    # conditional_format_rule
    AddConditionalFormatRule,
    DeleteConditionalFormatRule,
    UpdateConditionalFormatRule,
    ConditionalFormatRule,
    BooleanRule,
    BooleanCondition,
    ConditionType,
    ConditionValue,
    RelativeDate,
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
    DeleteDimension,
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

    # spreadsheet
    AddSheet,
    DeleteSheet,

    # general_models
    ColorStyle,
    GridRange,
    FieldMask,
    SimpleType,
)


class ApiRequest:
    @staticmethod
    def update_cells(
            sheet_id: int,
            range_: str,
            values: list[list[SimpleType]] | list[SimpleType] = None,
            cell_formats: list[list[CellFormat]] | list[CellFormat] = None
    ) -> dict:
        assert values or cell_formats, 'At least one of the parameters must be specified: values or cell_formats'
        start_row, end_row, start_col, end_col = ApiRequest._split_excel_range(range_)

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
    def add_boolean_format_rule(
            sheet_id: int,
            ranges: list[str],
            condition_type: ConditionType,
            *,
            condition_values: list[ConditionValue] = None,
            cell_format: CellFormat,
    ) -> dict:
        assert not any([
            cell_format.number_format, cell_format.borders, cell_format.padding,
            cell_format.horizontal_alignment, cell_format.vertical_alignment,
            cell_format.wrap_strategy, cell_format.text_direction, cell_format.text_rotation,
            cell_format.hyperlink_display_type
        ]), 'Conditional formatting can only apply a subset of formatting: bold, italic, strikethrough, foreground ' \
            'color and background color (background_color_style and text_format)'
        grid_ranges = [GridRange(sheet_id=sheet_id, **ApiRequest._split_excel_range(range_, return_as_dict=True)) for range_ in ranges]
        return AddConditionalFormatRule(rule=ConditionalFormatRule(
            ranges=grid_ranges,
            boolean_rule=BooleanRule(
                condition=BooleanCondition(
                    type=condition_type,
                    values=condition_values or []
                ),
                format=cell_format
            )
        )).dict()

    class GradientRule:
        IPTypeAndValue = tuple[InterpolationPointType, int | None]  # Type and Value of Interpolation Point

        @staticmethod
        def add(
                sheet_id: int,
                *,
                ranges: list[str],
                interpolation_points: tuple[IPTypeAndValue, IPTypeAndValue] | tuple[IPTypeAndValue, IPTypeAndValue, IPTypeAndValue],
                interpolation_point_colors: tuple[ColorStyle, ColorStyle] | tuple[ColorStyle, ColorStyle, ColorStyle],
        ) -> dict:
            assert len(interpolation_points) == len(interpolation_point_colors), 'The number of interpolation points must match the number of its colors'
            grid_ranges = [GridRange(sheet_id=sheet_id, **ApiRequest._split_excel_range(range_, return_as_dict=True)) for range_ in ranges]

            if len(interpolation_points) == 2:
                return AddConditionalFormatRule(rule=ConditionalFormatRule(
                    ranges=grid_ranges,
                    gradient_rule=GradientRule(
                        minpoint=InterpolationPoint(
                            color_style=interpolation_point_colors[0],
                            type=interpolation_points[0][0],
                            value=str(interpolation_points[0][1]) if interpolation_points[0][1] is not None else None
                        ),
                        maxpoint=InterpolationPoint(
                            color_style=interpolation_point_colors[1],
                            type=interpolation_points[1][0],
                            value=str(interpolation_points[1][1]) if interpolation_points[1][1] is not None else None
                        )
                    )
                )).dict()

            return AddConditionalFormatRule(rule=ConditionalFormatRule(
                ranges=grid_ranges,
                gradient_rule=GradientRule(
                    minpoint=InterpolationPoint(
                        color_style=interpolation_point_colors[0],
                        type=interpolation_points[0][0],
                        value=str(interpolation_points[0][1]) if interpolation_points[0][1] is not None else None
                    ),
                    midpoint=InterpolationPoint(
                        color_style=interpolation_point_colors[1],
                        type=interpolation_points[1][0],
                        value=str(interpolation_points[1][1]) if interpolation_points[1][1] is not None else None
                    ),
                    maxpoint=InterpolationPoint(
                        color_style=interpolation_point_colors[2],
                        type=interpolation_points[2][0],
                        value=str(interpolation_points[2][1]) if interpolation_points[2][1] is not None else None
                    )
                )
            )).dict()

        class Preset(StrEnum):
            # Two interpolation points
            WHITE_GREEN = 'WHITE_GREEN'
            WHITE_YELLOW = 'WHITE_YELLOW'
            WHITE_RED = 'WHITE_RED'
            GREEN_WHITE = 'GREEN_WHITE'
            YELLOW_WHITE = 'YELLOW_WHITE'
            RED_WHITE = 'RED_WHITE'

            # Three interpolation points
            RED_WHITE_GREEN_PERCENTILE = 'RED_WHITE_GREEN_PERCENTILE'
            RED_WHITE_GREEN_PERCENT = 'RED_WHITE_GREEN_PERCENT'
            GREEN_YELLOW_RED_PERCENTILE = 'GREEN_YELLOW_RED_PERCENTILE'
            GREEN_YELLOW_RED_PERCENT = 'GREEN_YELLOW_RED_PERCENT'
            GREEN_WHITE_RED_PERCENTILE = 'GREEN_WHITE_RED_PERCENTILE'
            GREEN_WHITE_RED_PERCENT = 'GREEN_WHITE_RED_PERCENT'
            RED_YELLOW_GREEN_PERCENTILE = 'RED_YELLOW_GREEN_PERCENTILE'
            RED_YELLOW_GREEN_PERCENT = 'RED_YELLOW_GREEN_PERCENT'

        @staticmethod
        def add_preset(sheet_id: int, ranges: list[str], preset: Preset) -> dict:
            grid_ranges = [GridRange(sheet_id=sheet_id, **ApiRequest._split_excel_range(range_, return_as_dict=True)) for range_ in ranges]
            AGP = ApiRequest.GradientRule.Preset

            # Two interpolation points presets
            if preset in (AGP.WHITE_GREEN, AGP.WHITE_YELLOW, AGP.WHITE_RED, AGP.GREEN_WHITE, AGP.YELLOW_WHITE, AGP.RED_WHITE):
                if preset == AGP.WHITE_YELLOW:
                    minpoint_color_style, maxpoint_color_style = Color_.Basic.WHITE, Color_.ConditionalFormatting.YELLOW
                elif preset == AGP.WHITE_RED:
                    minpoint_color_style, maxpoint_color_style = Color_.Basic.WHITE, Color_.ConditionalFormatting.RED
                elif preset == AGP.GREEN_WHITE:
                    minpoint_color_style, maxpoint_color_style = Color_.ConditionalFormatting.GREEN, Color_.Basic.WHITE
                elif preset == AGP.YELLOW_WHITE:
                    minpoint_color_style, maxpoint_color_style = Color_.ConditionalFormatting.YELLOW, Color_.Basic.WHITE
                elif preset == AGP.RED_WHITE:
                    minpoint_color_style, maxpoint_color_style = Color_.ConditionalFormatting.RED, Color_.Basic.WHITE
                else:  # preset == AGP.WHITE_GREEN and default
                    minpoint_color_style, maxpoint_color_style = Color_.Basic.WHITE, Color_.ConditionalFormatting.GREEN

                return AddConditionalFormatRule(rule=ConditionalFormatRule(
                    ranges=grid_ranges,
                    gradient_rule=GradientRule(
                        minpoint=InterpolationPoint(
                            color_style=minpoint_color_style,
                            type=InterpolationPointType.MIN,
                        ),
                        maxpoint=InterpolationPoint(
                            color_style=maxpoint_color_style,
                            type=InterpolationPointType.MAX,
                        )
                    )
                )).dict()

            else:  # Three interpolation points presets
                if preset in (AGP.RED_WHITE_GREEN_PERCENTILE, AGP.RED_WHITE_GREEN_PERCENT):
                    minpoint_cs, midpoint_cs, maxpoint_cs = Color_.ConditionalFormatting.RED, Color_.Basic.WHITE, Color_.ConditionalFormatting.GREEN
                    midpoint_type = InterpolationPointType.PERCENTILE if preset == AGP.RED_WHITE_GREEN_PERCENTILE else InterpolationPointType.PERCENT
                elif preset in (AGP.GREEN_YELLOW_RED_PERCENTILE, AGP.GREEN_YELLOW_RED_PERCENT):
                    minpoint_cs, midpoint_cs, maxpoint_cs = Color_.ConditionalFormatting.GREEN, Color_.ConditionalFormatting.YELLOW, Color_.ConditionalFormatting.RED
                    midpoint_type = InterpolationPointType.PERCENTILE if preset == AGP.GREEN_YELLOW_RED_PERCENTILE else InterpolationPointType.PERCENT
                elif preset in (AGP.GREEN_WHITE_RED_PERCENTILE, AGP.GREEN_WHITE_RED_PERCENT):
                    minpoint_cs, midpoint_cs, maxpoint_cs = Color_.ConditionalFormatting.GREEN, Color_.Basic.WHITE, Color_.ConditionalFormatting.RED
                    midpoint_type = InterpolationPointType.PERCENTILE if preset == AGP.GREEN_WHITE_RED_PERCENTILE else InterpolationPointType.PERCENT
                else:  # preset in (AGP.RED_YELLOW_GREEN_PERCENTILE, AGP.RED_YELLOW_GREEN_PERCENT):
                    minpoint_cs, midpoint_cs, maxpoint_cs = Color_.ConditionalFormatting.RED, Color_.ConditionalFormatting.YELLOW, Color_.ConditionalFormatting.GREEN
                    midpoint_type = InterpolationPointType.PERCENTILE if preset == AGP.RED_YELLOW_GREEN_PERCENTILE else InterpolationPointType.PERCENT

                return AddConditionalFormatRule(rule=ConditionalFormatRule(
                    ranges=grid_ranges,
                    gradient_rule=GradientRule(
                        minpoint=InterpolationPoint(
                            color_style=minpoint_cs,
                            type=InterpolationPointType.MIN,
                        ),
                        midpoint=InterpolationPoint(
                            color_style=midpoint_cs,
                            type=midpoint_type,
                            value=50
                        ),
                        maxpoint=InterpolationPoint(
                            color_style=maxpoint_cs,
                            type=InterpolationPointType.MAX,
                        )
                    )
                )).dict()

    @staticmethod
    def delete_conditional_format_rule(sheet_id: int, *, index: int) -> dict:
        return DeleteConditionalFormatRule(sheet_id=sheet_id, index=index).dict()

    @staticmethod
    def update_conditional_format_rule(sheet_id: int, *, index: int, rule: ConditionalFormatRule) -> dict:
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
        start_row, end_row, start_col, end_col = ApiRequest._split_excel_range(range_)
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
            *,
            range_: str = None,
            start_row: int = None,
            end_row: int = None,
            start_column: int | str = None,
            end_column: int | str = None,
    ) -> dict:
        assert range_ or (start_row and end_row and start_column and end_column), 'Either range_ or start_row, end_row, start_column, end_column must be specified'
        if range_:  # range_ has priority
            start_row, end_row, start_column, end_column = ApiRequest._split_excel_range(range_)
        else:
            start_column = ApiRequest._get_column_index(start_column) if isinstance(start_column, str) else start_column
            end_column = ApiRequest._get_column_index(end_column) if isinstance(end_column, str) else end_column
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
    def insert_rows(sheet_id: int, start_index: int, end_index: int = None, *, inherit_from_before: bool = True) -> dict:
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
    def insert_columns(sheet_id: int, start_index: int, end_index: int = None, *, inherit_from_before: bool = True) -> dict:
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
    def delete_rows(sheet_id: int, start_index: int, end_index: int = None):
        """
        Indexes are zero-based and inclusive [start_index, end_index]. If end_index is not specified, then a single
        row at start_index will be deleted.
        """
        end_index = end_index or start_index
        return DeleteDimension(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.ROWS,
                start_index=start_index,
                end_index=end_index + 1
            )
        ).dict()

    @staticmethod
    def delete_columns(sheet_id: int, start_index: int, end_index: int = None):
        """
        Indexes are zero-based and inclusive [start_index, end_index]. If end_index is not specified, then a single
        column at start_index will be deleted.
        """
        end_index = end_index or start_index
        return DeleteDimension(
            range=DimensionRange(
                sheet_id=sheet_id,
                dimension=Dimension.COLUMNS,
                start_index=start_index,
                end_index=end_index + 1
            )
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
            col_no = ApiRequest._get_column_index(col_no_or_letter)
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
            sheet_id: int = None,
            *,
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
    def _split_excel_range(range_: str, *, return_as_dict: bool = False) -> tuple[int, int, int, int] | dict[str, int]:
        if ':' in range_:
            match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)$', range_)
            if not match:
                raise ValueError(f'Unsupported range format: {range_}')
            start_column, start_row, end_column, end_row = match.groups()

        else:
            match = re.match(r'([A-Z]+)(\d+)$', range_)
            if not match:
                raise ValueError(f'Unsupported range format: {range_}')
            start_column, start_row = match.groups()
            end_column, end_row = start_column, start_row

        start_row, end_row = int(start_row), int(end_row)
        start_column, end_column = ApiRequest._get_column_index(start_column), ApiRequest._get_column_index(end_column)
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
    def _get_column_index(column_letters: str) -> int:
        column_index = 0
        for i, letter in enumerate(column_letters[::-1].upper()):
            column_index += (ord(letter) - 64) * (26 ** i)
        return column_index
