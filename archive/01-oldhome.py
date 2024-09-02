import plotly.graph_objects as go
import solara
import solara.lab
from loguru import logger

from hmtc.assets.colors import Colors
from hmtc.components.shared.sidebar import MySidebar
from hmtc.config import init_config
from hmtc.schemas.video import VideoItem

config = init_config()


@solara.component_vue("../components/shared/logo.vue")
def Logo():
    pass


def SubLogo(text):
    with solara.Row(classes=["sub-logo"]):
        solara.Text(text)


def tempPercentDownloadedGauge(current, total, on_click, on_hover):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=current,
            delta={"reference": total},
            gauge={"axis": {"visible": False}},
            domain={"row": 0, "column": 0},
        )
    )

    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)


def tempPercentDownloadedGauge2(stats, on_click, on_hover):
    logger.debug("About to create tempPercentDownloadedGauge2")

    fig = go.Figure()
    for s in stats:
        logger.debug(
            f"Stat: {s['name']} - downloaded = {s['downloaded']}  total={s['total']}"
        )

        fig.add_trace(
            go.Bar(
                y=[s["name"]],
                x=[s["downloaded"] / s["total"]] if s["total"] else [0],
                orientation="h",
                hovertemplate="%{y}<br>%{x:.0%} downloaded<extra></extra>",
                marker=dict(color=str(Colors.PRIMARY)),
            )
        )

    fig.update_layout(
        hoverlabel=dict(bgcolor="white", font_size=18, font_family="Rockwell"),
        yaxis=dict(title="Series"),
        showlegend=False,
        xaxis=dict(title="Percent Downloaded", tickformat=".0%"),
        title="Percent Downloaded by Series",
    )

    return solara.FigurePlotly(fig, on_click=on_click, on_hover=on_hover)


def prepare_stats(stats):
    logger.debug("Preparing stats")
    logger.debug(f"Stats: {stats}")
    return stats


@solara.component
def Page():
    MySidebar(
        router=solara.use_router(),
    )

    def on_click(*args):
        logger.info(f"click {args}")

    def on_hover(*args):
        # logger.info("hover")
        pass

    with solara.Column(classes=["main-container"]):
        with solara.Column(align="center"):
            stats = VideoItem.get_downloaded_stats_by_series()

            Logo()
            # SubLogo(text=f"all harry mack")
            # SubLogo(text=f"all the time...")
            with solara.Columns():
                # CompletionGauge(on_click=on_click, on_hover=on_hover)
                # tempPercentDownloadedGauge(
                #     current=50,
                #     total=100,
                #     on_click=on_click,
                #     on_hover=on_hover,
                # )
                tempPercentDownloadedGauge2(
                    stats=stats,
                    on_click=on_click,
                    on_hover=on_hover,
                )
