import plotly.express as px
import solara
from loguru import logger

# This dataframe has 244 lines, but 4 distinct values for `day`
df = px.data.tips()
fig = px.pie(df, values="tip", names="day")


from datetime import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px

df = pd.DataFrame(
    {
        "date": [
            "2022-01-07",
            "2022-02-07",
            "2022-03-07",
            "2022-04-07",
            "2022-05-07",
            "2022-06-07",
            "2022-07-07",
            "2022-08-07",
        ],
        "var1": [5, 7, 2, 4, 6, 8, 10, 9],
        "var2": [6, 7, 8, 5, 2, 6, 3, 1],
        "var3": [8, 5, 6, 2, 8, 3, 5, 4],
        "var4": [7, 9, 7, 5, 3, 4, 2, 1],
    }
)

df_melt = df.melt(
    id_vars=["date"],
    var_name="var",
    value_name="Amount",
    value_vars=df.columns[1:],
    ignore_index=True,
)

df_melt["%"] = (
    100 * df_melt["Amount"] / df_melt.groupby("date")["Amount"].transform("sum")
)

fig = px.bar(
    df_melt, x="date", y="%", color="var", title="Bar Plot", template="plotly_white"
)
fig.update_layout(barmode="relative")
fig.update_layout(plot_bgcolor="white")
fig.update_yaxes(showline=False, showgrid=False)
fig.update_xaxes(showline=False, showgrid=False)


import pandas as pd
import plotly.express as px


@solara.component
def StartFrequency(_range, times, on_click=None, on_hover=None):
    def handle_hover(*args):
        logger.error(f"Plotly Figure Component Hovered Over")
        logger.debug(f"args: {args}")
        on_hover(*args)

    def handle_click(*args):
        logger.error(f"Plotly Figure Component Clicked args={args}")
        on_click(*args)

    fig = px.scatter(
        x=times,
        y=[10] * len(times),
        title="",
        template="plotly_white",
    )
    fig.update_xaxes(range=_range)

    fig.update_layout(plot_bgcolor="white")

    # fig.update_layout(showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, range=[9, 11])
    fig.update_traces(marker=dict(size=30))

    fig.update_layout(
        width=800,
        height=200,
    )

    solara.FigurePlotly(fig)
