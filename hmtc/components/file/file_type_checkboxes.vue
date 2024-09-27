<template>
  <v-container class="" fluid>
    <v-row>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_info ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-information</v-icon>
          </v-chip>
        </template>
        <span>Youtube .info.json</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_info ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-panorama</v-icon>
          </v-chip>
        </template>
        <span>Poster</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_info ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-text</v-icon>
          </v-chip>
        </template>
        <span>Lyrics</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_audio ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-music-note</v-icon>
          </v-chip>
        </template>
        <span>Audio</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_video ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-video</v-icon>
          </v-chip>
        </template>
        <span>Video</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            :class="has_album_nfo ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-information</v-icon>
          </v-chip>
        </template>
        <span>Album NFO</span>
      </v-tooltip>
    </v-row>
    <v-row>
      <v-btn outlined @click="download_video" class="myprimary">
        <v-icon>mdi-download</v-icon>
        <span> Video</span>
      </v-btn>
      <!-- <v-btn outlined @click="download_info" class="mywarning">
            <v-icon>mdi-download</v-icon>
            <span> Download Info</span>
          </v-btn> -->

      <v-btn outlined @click="create_album_nfo" class="myprimary">
        <v-icon>mdi-hammer-wrench</v-icon>
        <span> Album NFO </span>
      </v-btn>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      has_audio: false,
      has_video: false,
      has_info: false,
      has_poster: false,
      has_subtitle: false,
      has_album_nfo: false,
    };
  },
  methods: {},
  mounted() {},
};
</script>
<style>
.mychecks {
  font-size: 1.4em;
  font-weight: 900;
  margin: 10px 10px 0px 0px;
}
</style>
