from dataclasses import dataclass
import solara
import polars as pl
import solara.express as px


@solara.component
def Page():
    file, set_file = solara.use_state(None)

    solara.Markdown("# Solara Example App (Starbucks Data)")
    solara.FileDrop(on_file=set_file, lazy=False)
    if file is not None:
        df = pl.read_csv(file["data"], null_values="-").drop_nulls()
        DFViews(df)
    else:
        solara.Text("Make sure to upload a file")


@dataclass
class FilterValues:
    sodium: tuple[int, int]
    carb: tuple[int, int]


@solara.component
def Filters(df: pl.DataFrame, filters: solara.Reactive[FilterValues]):
    with solara.Card("Filter DataFrame"):
        carbs = solara.use_reactive((df["Carb. (g)"].min(), df["Carb. (g)"].max()))
        sodium = solara.use_reactive((df["Sodium"].min(), df["Sodium"].max()))
        solara.SliderRangeInt(
            "Carbs (g)",
            value=carbs,
            min=df["Carb. (g)"].min(),
            max=df["Carb. (g)"].max(),
        )
        solara.SliderRangeInt(
            "Sodium", value=sodium, min=df["Sodium"].min(), max=df["Sodium"].max()
        )

        with solara.CardActions():
            solara.Button(
                "Submit",
                on_click=lambda: filters.set(FilterValues(sodium.value, carbs.value)),
            )


@solara.component
def FilteredPage(df: pl.DataFrame, filter_values: solara.Reactive[FilterValues]):
    df = df.filter(
        pl.col("Sodium").is_between(
            filter_values.value.sodium[0], filter_values.value.sodium[1]
        )
        & pl.col("Carb. (g)").is_between(
            filter_values.value.carb[0], filter_values.value.carb[1]
        )
    )
    DFVis(df)


@solara.component
def DFVis(df: pl.DataFrame):
    solara.Markdown(f"## DataFrame")
    solara.DataFrame(df.to_pandas(), items_per_page=5)
    px.histogram(df, x=["Carb. (g)", "Sodium"])


@solara.component
def DFViews(df: pl.DataFrame):
    filter_values = solara.use_reactive(
        FilterValues(
            (df["Carb. (g)"].min(), df["Carb. (g)"].max()),
            (df["Sodium"].min(), df["Sodium"].max()),
        )
    )
    Filters(df, filter_values)
    with solara.Columns():
        DFVis(df)
        FilteredPage(df, filter_values)
