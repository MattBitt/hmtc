import solara
import solara.lab
from typing import Any, Dict, List, cast
import ipyvuetify
import pandas as pd
import traitlets
import reacton.ipyvuetify as v

# to avoid confusing vuetify about selecting 'None' and nothing
magic_value_missing = "__missing_value__"

# first selector is needed in jupyter, which needs to be more specific
# second selector in solara, where there is no need to be more specific (css load order?) and there is not .vuetify-styles
css_message = """
.vuetify-styles .solara-cross-filter-select .v-messages,
.solara-cross-filter-select .v-messages {
    color: #fb8c00;
}
"""


class Select(ipyvuetify.VuetifyTemplate):
    template_file = (__file__, "select.vue")

    value = traitlets.Any().tag(sync=True)
    label = traitlets.Unicode().tag(sync=True)
    clearable = traitlets.Bool().tag(sync=True)
    return_object = traitlets.Bool().tag(sync=True)
    items = traitlets.List(cast(List[Dict[str, Any]], [])).tag(sync=True)
    filtered = traitlets.Bool().tag(sync=True)
    count = traitlets.Int().tag(sync=True)
    multiple = traitlets.Bool().tag(sync=True)
    messages = traitlets.Unicode().tag(sync=True)


def get_pandas_major():
    import pandas as pd

    return int(pd.__version__[0])


def df_type(df):
    return df.__class__.__module__.split(".")[0]


def use_df_column_names(df):
    if df_type(df) == "vaex":
        return df.get_column_names()
    elif df_type(df) == "pandas":
        return df.columns.tolist()
    elif df_type(df) == "polars":
        return df.columns
    else:
        raise TypeError(f"{type(df)} not supported")


def df_value_count(df, column, limit=None):
    if df_type(df) == "vaex":
        dfv = df.groupby(column, agg="count", sort="count", ascending=False)
        dfv = dfv.to_pandas_df().rename({column: "value"}, axis=1)
        return dfv[:limit]
    if df_type(df) == "pandas":
        dfv = df[column].value_counts(dropna=False).to_frame()
        dfv = dfv.reset_index()
        if get_pandas_major() >= 2:
            dfv = dfv.rename({column: "value"}, axis=1)
        else:
            dfv = dfv.rename({"index": "value", column: "count"}, axis=1)
        return dfv[:limit]
    else:
        raise TypeError(f"{type(df)} not supported")


def df_filter_values(df, column, values, invert=False):
    if df_type(df) == "vaex":
        filter = df[column].isin(values)
        if invert:
            filter = ~filter
        return filter
    if df_type(df) == "pandas":
        filter = df[column].isin(values)
        if invert:
            filter = ~filter
        return filter
    else:
        raise TypeError(f"{type(df)} not supported")


@solara.component
def CrossFilterSelect(
    df,
    column: str,
    max_unique: int = 100,
    multiple: bool = False,
    invert=False,
    configurable=False,
    classes: List[str] = [],
):
    """A Select widget that will cross filter a DataFrame.

    See [use_cross_filter](/documentation/api/hooks/use_cross_filter) for more information about how to use cross filtering.

    ## Arguments

    - `df`: The DataFrame to filter.
    - `column`: The column to filter on.
    - `max_unique`: The maximum number of unique values to show in the dropdown.
    - `multiple`: Whether to allow multiple values to be selected.
    - `invert`: Whether to invert the selection.
    - `configurable`: Whether to show the configuration button.
    - `classes`: Additional CSS classes to add to the main widget.

    """

    filter, set_filter = solara.use_cross_filter(id(df), "filter-dropdown")
    filter_values, set_filter_values = solara.use_state(cast(List[Any], []))
    column, set_column = solara.use_state_or_update(column)
    invert, set_invert = solara.use_state_or_update(invert)
    multiple, set_multiple = solara.use_state_or_update(multiple)

    dff = df
    if filter is not None:
        dff = df[filter]

    value_counts = df_value_count(df, column, limit=max_unique + 1)
    value_counts.rename({"count": "count_max"}, axis=1, inplace=True)

    value_counts_filtered = df_value_count(dff, column, limit=max_unique + 1)
    value_counts = value_counts.merge(value_counts_filtered, how="left", on="value")
    value_counts["count"] = value_counts["count"].fillna(0)
    value_counts["exists"] = value_counts["count"] > 0
    value_counts.sort_values(["exists", "value"], ascending=[False, True], inplace=True)

    columns = use_df_column_names(df)

    def set_values_and_filter(values):
        if values is None:
            set_filter_values([])
            return

        if multiple:
            set_filter_values([value["value"] for value in values])
        else:
            set_filter_values([values["value"]])

    def reset():
        set_filter_values([])

    solara.use_memo(reset, dependencies=[column])

    def update_filter():
        if len(filter_values) == 0:
            set_filter(None)
        else:
            filter_values_without_magic = [
                None if k == magic_value_missing else k for k in filter_values
            ]
            filter = df_filter_values(
                df, column, filter_values_without_magic, invert=invert
            )
            set_filter(filter)

    solara.use_memo(update_filter, dependencies=[filter_values, invert])

    items = [
        {
            "value": magic_value_missing if pd.isna(k.value) else k.value,
            "text": str(k.value) if not pd.isna(k.value) else "NA",
            "count": k.count,
            "count_max": k.count_max,
        }
        for k in value_counts.itertuples()
    ]
    value: Any = None
    if not multiple:
        value = {"value": filter_values[0]} if len(filter_values) > 0 else None
    else:
        value = [{"value": k} for k in filter_values]
    # TODO: reacton bug, we cannot add this under any component context manager
    # this gives an error, probably because the button is added twice
    with v.Btn(v_on="x.on", icon=True) as btn:
        v.Icon(children=["mdi-settings"])
    with solara.VBox(classes=classes) as main:
        solara.Style(css_message)
        with solara.HBox(align_items="baseline"):
            label = f"{column}" if not invert else f"{column}"
            Select.element(
                value=value,
                items=items,
                on_value=set_values_and_filter,
                label=label,
                clearable=True,
                return_object=True,
                multiple=multiple,
                filtered=filter is not None,
                count=len(dff),
                messages=(
                    f"Too many unique values, will only show the first {max_unique}"
                    if len(value_counts) > max_unique
                    else ""
                ),
                class_="solara-cross-filter-select",
            )
            if configurable:
                with v.Menu(
                    v_slots=[{"name": "activator", "variable": "x", "children": btn}],
                    close_on_content_click=False,
                ):
                    with v.Sheet():
                        with v.Container(py_0=True, px_3=True, ma_0=True):
                            with v.Row():
                                with v.Col():
                                    v.Select(
                                        v_model=column,
                                        items=columns,
                                        on_v_model=set_column,
                                        label="Choose column",
                                    )
                                    v.Switch(
                                        v_model=invert,
                                        on_v_model=set_invert,
                                        label="Invert filter",
                                    )
                                    v.Switch(
                                        v_model=multiple,
                                        on_v_model=set_multiple,
                                        label="Select multiple",
                                    )

    return main
