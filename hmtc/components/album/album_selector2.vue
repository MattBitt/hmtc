<!-- <template>
  <v-card class="overflow-hidden" color="">
    <v-toolbar flat color="">
      <v-icon>mdi-information</v-icon>
      <v-toolbar-title class="font-weight-light">
        Video Information
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn class="myprimary" fab small @click="isEditing = !isEditing">
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
      <AutoComplete
        v-model="selectedAlbum"
        :items="albums"
        label="Album"
        itemText="title"
        itemValue="id"
        icon="mdi-album"
        :isEditing="isEditing"
        :placeholder="this.selectedAlbum"
        @addNewItem="addNewAlbum"
        @selectItem="selectAlbum"
        @clearItem="clearAlbum"
      >
      </AutoComplete>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn :disabled="!isEditing" class="button" @click="save"> Save </v-btn>
    </v-card-actions>
    <v-snackbar v-model="hasSaved" :timeout="2000" absolute bottom left>
      Your profile has been updated
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

  methods: {
    customFilter(item, queryText, itemText) {
      const textOne = item.title.toLowerCase();
      // const textTwo = item.abbr.toLowerCase()
      const searchText = queryText.toLowerCase();

      return textOne.indexOf(searchText) > -1;
    },
    save() {
      const args = {
        album: this.selectedAlbum,
        youtube_series: this.selectedYoutubeSeries,
        series: this.selectedSeries,
        episode_number: this.episode_number,
      };
      this.isEditing = !this.isEditing;
      this.hasSaved = true;
      this.update_video(args);
    },
    addNewAlbum(albumTitle) {
      console.log("adding new album (parent)", albumTitle);
      // call python here
      this.searchQ = "";
      this.albums.push({ title: albumTitle, id: this.albums.length + 1 });
      // this.albums.push({ title: 'New Album', id: this.albums.length + 1 })
      // this.model = this.albums[this.albums.length - 1]
    },
    selectAlbum(val) {
      console.log("selected album (parent)", val);
      this.selectedAlbum = val.title;
    },
    clearAlbum() {
      console.log("clearing album (parent)");
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
</script> -->
