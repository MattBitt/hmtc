import solara
from solara import CellAction, ColumnAction
from typing import Any, Dict, List, Optional, cast


@solara.component
def FilteredDataFrame(
    df,
    items_per_page=100,
    column_actions: List[ColumnAction] = [],
    cell_actions: List[CellAction] = [],
    scrollable=False,
):
    """Display a DataFrame with filters applied from the cross filter.

    This component wraps [DataFrame](/documentation/components/data/dataframe).

    See [use_cross_filter](/documentation/api/hooks/use_cross_filter) for more information about how to use cross filtering.

    # Arguments

     * `df` - a Pandas dataframe.
     * `column_actions` - Triggered via clicking on the triple dot icon on the headers (visible when hovering).
     * `cell_actions` -  Triggered via clicking on the triple dot icon in the cell (visible when hovering).

    """
    dff = df
    filter, set_filter = solara.use_cross_filter(id(df), "dataframe")
    if filter is not None:
        dff = df[filter]
    return solara.DataFrame(
        dff,
        items_per_page=items_per_page,
        scrollable=scrollable,
        column_actions=column_actions,
        cell_actions=cell_actions,
    )
