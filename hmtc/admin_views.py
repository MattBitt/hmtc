import peewee
from flask import Flask

import flask_admin as admin
from flask_admin.contrib.peewee import ModelView

from hmtc.models import (
    User,
    UserInfo,
    Post,
    Playlist,
    Video,
    Series,
    Album,
    Track,
    EpisodeNumberTemplate,
    File,
    Artist,
    Beat,
    BeatArtist,
    TrackBeat,
    Section,
)


class UserAdmin(ModelView):
    inline_models = (UserInfo,)

    @classmethod
    def view(cls):
        return cls(User)


class PostAdmin(ModelView):
    # Visible columns in the list view
    column_exclude_list = ["text"]

    # List of columns that can be sorted. For 'user' column, use User.email as
    # a column.
    column_sortable_list = ("title", ("user", User.email), "date")

    # Full text search
    column_searchable_list = ("title", User.username)

    # Column filters
    column_filters = ("title", "date", User.username)

    form_ajax_refs = {"user": {"fields": (User.username, "email")}}

    @classmethod
    def view(cls):
        return cls(Post)


# Playlist Admin View
class PlaylistAdmin(ModelView):
    column_filters = ["name", "enabled", "last_update_completed"]
    form_columns = [
        "name",
        "url",
        "album_per_episode",
        "enabled",
        "album",
        "series",
        "last_update_completed",
    ]
    column_searchable_list = ["name", "url"]
    form_ajax_refs = {
        "album": {"fields": ("name",), "page_size": 10},
        "series": {"fields": ("name",), "page_size": 10},
    }

    @classmethod
    def view(cls):
        return cls(Playlist)


class SeriesAdmin(ModelView):
    column_filters = ["name", "start_date", "end_date"]
    form_columns = [
        "name",
        "start_date",
        "end_date",
    ]
    column_searchable_list = ["name"]
    form_ajax_refs = {
        "playlist": {"fields": ("name",), "page_size": 10},
        "videos": {"fields": ("title",), "page_size": 10},
    }

    @classmethod
    def view(cls):
        return cls(Series)


# Playlist Admin View
class VideoAdmin(ModelView):
    column_exclude_list = ["description"]
    column_filters = [
        "youtube_id",
        "title",
        "episode",
        "upload_date",
        "duration",
        "private",
        "error",
        "error_info",
    ]
    form_columns = [
        "youtube_id",
        "title",
        "episode",
        "upload_date",
        "duration",
        "private",
        "error",
        "error_info",
    ]
    column_searchable_list = [
        "youtube_id",
        "title",
        "episode",
    ]

    @classmethod
    def view(cls):
        return cls(Video)
