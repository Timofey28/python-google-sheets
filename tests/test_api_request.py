
import pytest

from google_sheets import ApiRequest


def test_add_sheet_default_group_controls():
    """Default group controls must be placed after groups."""
    result = ApiRequest.add_sheet(
        sheet_id=123,
        title='Test'
    )

    properties = result["addSheet"]["properties"]
    grid = properties["gridProperties"]

    assert grid["rowGroupControlAfter"] is True
    assert grid["columnGroupControlAfter"] is True


def test_add_sheet_group_controls_before():
    """Both controls can be placed before groups."""
    result = ApiRequest.add_sheet(
        sheet_id=123,
        title='Test',
        row_group_control_after=False,
        column_group_control_after=False
    )

    grid = result["addSheet"]["properties"]["gridProperties"]

    assert grid["rowGroupControlAfter"] is False
    assert grid["columnGroupControlAfter"] is False


@pytest.mark.parametrize(
    'row_after,column_after',
    [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ]
)
def test_add_sheet_group_control_combinations(
    row_after,
    column_after
):
    """Row and column settings must be independent."""
    result = ApiRequest.add_sheet(
        row_group_control_after=row_after,
        column_group_control_after=column_after
    )

    grid = result["addSheet"]["properties"]["gridProperties"]

    assert grid["rowGroupControlAfter"] is row_after
    assert grid["columnGroupControlAfter"] is column_after


def test_add_sheet_preserves_existing_properties():
    """New parameters must not break existing sheet properties."""
    result = ApiRequest.add_sheet(
        sheet_id=123,
        title='Test sheet',
        index=0,
        hidden=False,
        row_count=100,
        column_count=10,
        frozen_row_count=1,
        frozen_column_count=2,
        hide_grid_lines=True,
        row_group_control_after=False,
        column_group_control_after=True
    )

    properties = result["addSheet"]["properties"]
    grid = properties["gridProperties"]

    assert properties["sheetId"] == 123
    assert properties["title"] == "Test sheet"
    assert properties["index"] == 0
    assert properties["hidden"] is False

    assert grid["rowCount"] == 100
    assert grid["columnCount"] == 10
    assert grid["frozenRowCount"] == 1
    assert grid["frozenColumnCount"] == 2
    assert grid["hideGridlines"] is True
    assert grid["rowGroupControlAfter"] is False
    assert grid["columnGroupControlAfter"] is True
