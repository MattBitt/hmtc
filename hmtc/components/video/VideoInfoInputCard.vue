<template>
  <v-card flat class="overflow-hidden" color="">
    <v-card-text>
      <v-row justify="center">
        <v-col cols="8">
          <h3>{{ albumDict.title ? albumDict.title : "" }}</h3>
        </v-col>
        <v-col cols="4">
          <AlbumPanel
            :items="albums"
            :hasAlbum="thisVidHasAlbum"
            :albumInfo="albumDict"
            :possibleAlbumTitle="constructAlbumTitle()"
            @createAlbum="createAlbum"
            @selectAlbum="selectAlbum"
            @removeAlbum="removeAlbum"
          />
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="8">
          <h3>{{ this.selectedSeries }}</h3>
        </v-col>
        <v-col cols="4">
          <SeriesPanel
            :items="serieses"
            :hasSeries="true"
            :seriesInfo="seriesDict"
            @createSeries="createSeries"
            @selectSeries="selectSeries"
            @removeSeries="removeSeries"
          />
        </v-col>
      </v-row>
      <v-row justify="center">
        <v-col cols="8">
          <h3>{{ this.selectedYoutubeSeries }}</h3>
        </v-col>
        <v-col cols="4">
          <YoutubeSeriesPanel
            :items="youtube_serieses"
            :hasYoutubeSeries="true"
            :youtubeseriesInfo="youtubeSeriesDict"
            @createYoutubeSeries="createYoutubeSeries"
            @selectYoutubeSeries="selectYoutubeSeries"
            @removeYoutubeSeries="removeYoutubeSeries"
          />
        </v-col>
      </v-row>
      <v-row justify="center">
        <h2>VideoFiles Dialog Should go here when ready.</h2>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
    </v-card-actions>
  </v-card>
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
      const album = this.albums.find((a) => a.title === this.selectedAlbum);
      const ad = album ? album : { title: null, release_date: null };
      console.log("albumDict", ad);
      return ad;
    },
    seriesDict() {
      console.log("seriesDict");
      return { name: this.selectedSeries };
    },

    youtubeSeriesDict() {
      console.log("youtubeseriesDict");
      return { title: this.selectedYoutubeSeries };
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
    removeAlbum(args) {
      this.selectedAlbum = null;
      this.albums = this.albums.filter((a) => a.title !== args.title);
      this.remove_album_from_video(args);
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

    constructAlbumTitle() {
      console.log(
        "possibleAlbumTfdsafsdfsditle",
        this.selectedYoutubeSeries,
        this.episode_number
      );
      const newName = `${
        this.selectedYoutubeSeries
      } ${this.episode_number?.padStart(3, "0")}`;
      console.log("newName", newName);
      return newName;
    },
  },
  watch: {},
};
</script>
