<template>
  <v-row justify="center">
    <v-col>
      <AlbumPanel
        :items="albums"
        :hasAlbum="true"
        :albumInfo="albumDict"
        @createAlbum="createAlbum"
        @selectAlbum="selectAlbum"
        @removeAlbum="removeAlbum"
      />
      <h4>{{ albumDict?.title }}</h4>
    </v-col>

    <v-col>
      <SeriesPanel
        :items="serieses"
        :hasSeries="true"
        :seriesInfo="seriesDict"
        @createSeries="createSeries"
        @selectSeries="selectSeries"
        @removeSeries="removeSeries"
      />
      <h4>{{ this.selectedSeries?.name }}</h4>
    </v-col>

    <v-col>
      <YoutubeSeriesPanel
        :items="youtube_serieses"
        :hasYoutubeSeries="true"
        :youtubeseriesInfo="youtubeSeriesDict"
        @createYoutubeSeries="createYoutubeSeries"
        @selectYoutubeSeries="selectYoutubeSeries"
        @removeYoutubeSeries="removeYoutubeSeries"
      />
      <h4>{{ this.selectedYoutubeSeries?.title }}</h4>
    </v-col>
  </v-row>
</template>

<script>
export default {
  data() {
    return {
      model: null,
      selectedAlbum: 0,
      selectedYoutubeSeries: 0,
      selectedSeries: 0,
      episode_number: 0,
    };
  },
  computed: {
    albumDict() {
      return this.selectedAlbum;
    },
    seriesDict() {
      return this.selectedSeries;
    },

    youtubeSeriesDict() {
      return this.selectedYoutubeSeries;
    },
  },
  methods: {
    createAlbum(args) {
      this.selectedAlbum = { title: args.title };
      this.albums.push(this.selectedAlbum);
      this.create_album(this.selectedAlbum);
    },

    createYoutubeSeries(args) {
      this.selectedYoutubeSeries = {
        title: args.title,
      };
      this.youtube_serieses.push(this.selectedYoutubeSeries);
      this.create_youtube_series(this.selectedYoutubeSeries);
    },
    createSeries(args) {
      this.selectedSeries = { name: args.name };
      this.serieses.push(this.selectedSeries);
      this.create_series(this.selectedSeries);
    },

    selectAlbum(val) {
      this.selectedAlbum = { title: val.title, id: val.id };
      this.update_album_for_video(this.selectedAlbum);
    },

    selectSeries(val) {
      this.selectedSeries = { name: val.name, id: val.id };
      this.update_series_for_video(this.selectedSeries);
    },
    selectYoutubeSeries(val) {
      this.selectedYoutubeSeries = { title: val.title, id: val.id };
      this.update_youtube_series_for_video(this.selectedYoutubeSeries);
    },
    removeAlbum() {
      this.albums = this.albums.filter((a) => a.title !== this.selectedAlbum);
      this.selectedAlbum = null;

      this.remove_album_from_video();
    },

    removeSeries() {
      this.remove_series_from_video();
    },
    removeYoutubeSeries() {
      this.remove_youtube_series_from_video();
    },
  },
  watch: {},
  created() {},
};
</script>
