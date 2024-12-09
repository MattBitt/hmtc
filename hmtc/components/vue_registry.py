import ipyvue


def register_vue_components(file):

    ipyvue.register_component_from_file(
        "AutoComplete", "../../components/shared/AutoComplete.vue", file
    )

    ipyvue.register_component_from_file(
        "MyToolTipChip",
        "../../components/shared/MyToolTipChip.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "AlbumPanel",
        "../../components/video/AlbumPanel.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "SeriesPanel",
        "../../components/video/SeriesPanel.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "YoutubeSeriesPanel",
        "../../components/video/YoutubeSeriesPanel.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "VideoFilesDialog",
        "../../components/video/file_type_checkboxes.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "VideoFilesInfoModal",
        "../../components/video/VideoFilesInfoModal.vue",
        file,
    )
    ipyvue.register_component_from_file(
        "SummaryPanel",
        "../../components/section/SummaryPanel.vue",
        file,
    )

    ipyvue.register_component_from_file(
        "SectionAdminPanel", "../../components/section/admin_panel.vue", file
    )

    ipyvue.register_component_from_file(
        "SectionTopicsPanel", "../../components/section/topics_panel.vue", file
    )

    ipyvue.register_component_from_file(
        "SectionTimePanel", "../../components/section/time_panel.vue", file
    )

    ipyvue.register_component_from_file(
        "BeatsInfo", "../../components/beat/beats_info.vue", file
    )
    ipyvue.register_component_from_file(
        "ArtistsInfo", "../../components/artist/artists_info.vue", file
    )
    ipyvue.register_component_from_file(
        "SectionTrackPanel", "../../components/video/SectionTrackPanel.vue", file
    )

    ipyvue.register_component_from_file(
        "SectionTrackForm", "../../components/video/SectionTrackForm.vue", file
    )
