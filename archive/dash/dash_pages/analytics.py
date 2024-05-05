import dash
import pandas as pd
from dash import html

from hmtc.models import Video

dash.register_page(__name__)


def seconds_to_hms(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return hours, minutes, seconds


def get_total_duration(df):
    return seconds_to_hms(df.sum()[0])


def get_library_stats():
    query = Video.select(Video.duration).where(Video.duration.is_null(False))
    df = pd.DataFrame([q.duration for q in query])

    h, m, s = get_total_duration(df)
    stats = {
        "total_duration": f"{h} hours, {m} minutes, and {s} seconds",
        "num_videos": len(df),
    }
    return stats


stats = get_library_stats()
layout = html.Div(
    [
        html.H2("Harry Mack Videos in Database"),
        html.H1((f"{stats['num_videos']} Videos"), id="num-videos-output"),
        html.H1((stats["total_duration"]), id="duration-output"),
        html.Br(),
        html.Div(id="analytics-output"),
    ]
)
