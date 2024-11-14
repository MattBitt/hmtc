<template>
  <v-row justify="center">
    <v-col>
      <AlbumPanel
        :items="albums"
        :hasAlbum="albumDict.id != 0"
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
        :hasSeries="seriesDict.id != 0"
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
        :hasYoutubeSeries="youtubeSeriesDict?.id != 0"
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
      console.log("createAlbum type/args passed in", args);
      this.selectedAlbum = { title: args.title };
      this.albums.push(this.selectedAlbum);
      const _args = {
        type: "album",
        item: this.selectedAlbum,
      };
      this.create(_args);
    },

    createSeries(args) {
      this.selectedSeries = { name: args.name };
      this.serieses.push(this.selectedSeries);
      const _args = {
        type: "series",
        item: this.selectedSeries,
      };
      this.create(_args);
    },

    createYoutubeSeries(args) {
      this.selectedYoutubeSeries = {
        title: args.title,
      };
      this.youtube_serieses.push(this.selectedYoutubeSeries);
      const _args = {
        type: "youtube_series",
        item: this.selectedYoutubeSeries,
      };
      this.create(_args);
    },

    selectAlbum(val) {
      this.selectedAlbum = { title: val.title, id: val.id };
      const _args = {
        type: "album",
        item: this.selectedAlbum,
      };
      this.update(_args);
    },

    selectSeries(val) {
      this.selectedSeries = { name: val.name, id: val.id };
      const _args = {
        type: "series",
        item: this.selectedSeries,
      };
      this.update(_args);
    },
    selectYoutubeSeries(val) {
      this.selectedYoutubeSeries = { title: val.title, id: val.id };
      const _args = {
        type: "youtube_series",
        item: this.selectedYoutubeSeries,
      };
      this.update(_args);
    },
    removeAlbum() {
      this.albums = this.albums.filter((a) => a.title !== this.selectedAlbum);

      const _args = {
        type: "album",
        item: this.selectedAlbum,
      };

      this.remove(_args);
      this.selectedAlbum = null;
    },

    removeSeries() {
      this.serieses = this.serieses.filter(
        (a) => a.name !== this.selectedSerieses
      );

      const _args = {
        type: "series",
        item: this.selectedSeries,
      };
      this.remove(_args);
      this.selectedSerieses = null;
    },
    removeYoutubeSeries() {
      this.youtube_serieses = this.youtube_serieses.filter(
        (a) => a.title !== this.selectedYoutubeSeries
      );

      const _args = {
        type: "youtube_series",
        item: this.selectedYoutubeSeries,
      };
      this.remove(_args);
      this.selectedYoutubeSeries = null;
    },
  },
  watch: {},
  created() {},
};
</script>
