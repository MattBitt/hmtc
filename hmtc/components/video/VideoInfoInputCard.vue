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
      <h4>{{ albumDict.title ? albumDict.title : "" }}</h4>
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
      <h4>{{ this.selectedSeries.name }}</h4>
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
      <h4>{{ this.selectedYoutubeSeries.title }}</h4>
    </v-col>
  </v-row>
</template>

<script>
export default {
  data() {
    return {
      model: null,
      selectedAlbum: null,
      selectedYoutubeSeries: null,
      selectedSeries: null,
      episode_number: null,
    };
  },
  computed: {
    albumDict() {
      console.log("albumDict");
      return this.selectedAlbum;
    },
    seriesDict() {
      console.log("seriesDict");
      return this.selectedSeries;
    },

    youtubeSeriesDict() {
      console.log("youtubeseriesDict");
      return this.selectedYoutubeSeries;
    },
    thisVidHasAlbum() {
      return this.selectedAlbum !== null;
    },
  },
  methods: {
    createAlbum(args) {
      console.log("In VideoInfoInputCard createAlbum", args);

      this.albums.push(args);
      this.selectedAlbum = args.title;
      this.create_album(args);
    },
    removeAlbum() {
      console.log("In VideoInfoInputCard removeAlbum", this.selectedAlbum);
      this.albums = this.albums.filter((a) => a.title !== this.selectedAlbum);
      this.selectedAlbum = null;

      this.remove_album_from_video();
    },

    selectAlbum(val) {
      this.selectedAlbum = val.title;
      const args = {
        title: this.selectedAlbum,
      };
      this.update_album_for_video(args);
    },

    createYoutubeSeries(youtubeseriesTitle) {
      console.log("adding new youtubeseries (parent)", youtubeseriesTitle);
      this.youtube_serieses.push({
        title: youtubeseriesTitle,
        id: this.youtube_serieses.length + 1,
      });
      this.create_youtube_series(youtubeseriesTitle);
      // this.youtube_serieses.push({ title: 'New YoutubeSeries', id: this.youtube_serieses.length + 1 })
      // this.model = this.youtube_serieses[this.youtube_serieses.length - 1]
    },
    removeYoutubeSeries() {
      console.log("clearing youtubeseries (parent)");
      this.remove_youtube_series_from_video();
    },
    selectYoutubeSeries(val) {
      console.log("selected youtubeseries (parent)", val);
      this.selectedYoutubeSeries = val.title;

      const args = {
        title: this.selectedYoutubeSeries,
      };
      this.update_youtube_series_for_video(args);
    },

    createSeries(seriesName) {
      console.log("adding new series (parent)", seriesName);
      this.serieses.push({
        name: seriesName,
        id: this.serieses.length + 1,
      });
      this.create_series(seriesName);
    },
    removeSeries() {
      console.log("clearing series (parent)");
      this.remove_series_from_video();
    },
    selectSeries(val) {
      console.log("selected series (parent)", val);
      this.selectedSeries = val.name;
      this.update_series_for_video(val);
    },
  },
  watch: {},
  created() {
    console.log("In VideoInfoInputCard created");
    console.log("selectedAlbum", this.selectedAlbum);
    console.log("selectedSeries", this.selectedSeries);
    console.log("selectedYoutubeSeries", this.selectedYoutubeSeries);
  },
};
</script>
