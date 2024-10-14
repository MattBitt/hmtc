<template>
  <v-card flat class="overflow-hidden" color="">
    <v-toolbar flat class="">
      <v-spacer></v-spacer>
      <v-btn v-if="isEditing" color="primary" fab small @click="save">
        <v-icon>mdi-content-save</v-icon>
      </v-btn>
      <v-btn
        :color="isEditing ? 'primary' : 'warning'"
        fab
        small
        @click="isEditing = !isEditing"
      >
        <v-icon v-if="isEditing"> mdi-close </v-icon>
        <v-icon v-else> mdi-pencil </v-icon>
      </v-btn>
    </v-toolbar>
    <v-card-text>
      <AutoComplete
        v-model="selectedSeries"
        :items="serieses"
        label="Series"
        itemText="name"
        itemValue="id"
        icon="mdi-shape"
        :isEditing="isEditing"
        :placeholder="this.selectedSeries"
        @addNewItem="addNewSeries"
        @selectItem="selectSeries"
        @clearItem="clearSeries"
      >
      </AutoComplete>
      <v-row>
        <v-col cols="12" sm="8">
          <AutoComplete
            v-model="selectedYoutubeSeries"
            :items="youtube_serieses"
            label="Youtube Series"
            itemText="title"
            itemValue="id"
            icon="mdi-youtube"
            :isEditing="isEditing"
            :placeholder="this.selectedYoutubeSeries"
            @addNewItem="addNewYoutubeSeries"
            @selectItem="selectYoutubeSeries"
            @clearItem="clearYoutubeSeries"
          >
          </AutoComplete>
        </v-col>
        <v-col cols="4">
          <v-text-field
            v-model="episode_number"
            label="Episode"
            :disabled="!isEditing"
          ></v-text-field>
        </v-col>
      </v-row>

      <v-row justify="center">
        <AlbumPanel
          :items="albums"
          :hasAlbum="thisVidHasAlbum"
          :albumInfo="albumDict"
          :possibleAlbumTitle="constructAlbumTitle()"
          @createAlbum="createAlbum"
          @selectAlbum="chooseExistingAlbum"
          @removeAlbum="removeAlbum"
        />
        <h3>{{ albumDict }}</h3>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
    </v-card-actions>
    <v-snackbar v-model="hasSaved" :timeout="2000" absolute bottom left>
      Video has been updated
    </v-snackbar>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      hasSaved: false,
      isEditing: false,
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
    thisVidHasAlbum() {
      return this.selectedAlbum !== null;
    },
  },
  methods: {
    save() {
      const args = {
        album: null, //deprecated and moved to button
        youtube_series: this.selectedYoutubeSeries,
        series: this.selectedSeries,
        episode_number: this.episode_number,
      };
      this.isEditing = !this.isEditing;
      this.hasSaved = true;
      this.update_video(args);
    },
    createAlbum(args) {
      this.create_album(args);
      this.selectedAlbum = args.title;
    },
    removeAlbum(args) {
      this.remove_album_from_video(args);
      this.selectedAlbum = null;
    },

    chooseExistingAlbum(val) {
      this.selectedAlbum = val.title;
      const args = {
        title: this.selectedAlbum,
      };
      this.update_album_for_video(args);
    },
    constructAlbumTitle() {
      console.log(
        "possibleAlbumTfdsafsdfsditle",
        this.selectedYoutubeSeries,
        this.episode_number
      );
      if (true) {
        const newName = `${
          this.selectedYoutubeSeries
        } ${this.episode_number.padStart(3, "0")}`;
        console.log("newName", newName);
        return newName;
      } else {
        console.log(
          "Couldn't create newName",
          this.selectedYoutubeSeries,
          " - ",
          this.episode_number
        );
        return null;
      }
    },

    addNewYoutubeSeries(youtubeseriesTitle) {
      console.log("adding new youtubeseries (parent)", youtubeseriesTitle);
      // call python here
      this.searchQ = "";
      this.youtubeseriess.push({
        title: youtubeseriesTitle,
        id: this.youtubeseriess.length + 1,
      });
      // this.youtubeseriess.push({ title: 'New YoutubeSeries', id: this.youtubeseriess.length + 1 })
      // this.model = this.youtubeseriess[this.youtubeseriess.length - 1]
    },
    selectYoutubeSeries(val) {
      console.log("selected youtubeseries (parent)", val);
      this.selectedYoutubeSeries = val.title;
    },
    clearYoutubeSeries() {
      console.log("clearing youtubeseries (parent)");
    },
    addNewSeries(seriesName) {
      console.log("adding new series (parent)", seriesName);
      // call python here
      this.searchQ = "";
      this.youtubeseriess.push({
        name: seriesName,
        id: this.seriess.length + 1,
      });
      // this.youtubeseriess.push({ title: 'New YoutubeSeries', id: this.youtubeseriess.length + 1 })
      // this.model = this.youtubeseriess[this.youtubeseriess.length - 1]
    },
    selectSeries(val) {
      console.log("selected series (parent)", val);
      this.selectedSeries = val.name;
    },
    clearSeries() {
      console.log("clearing series (parent)");
    },
  },
  watch: {},
};
</script>
