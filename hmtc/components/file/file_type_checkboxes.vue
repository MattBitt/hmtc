<template>
  <v-sheet fluid>
    <v-container class="">
      <v-row align-items="right">
        <v-col class="d-flex flex-column mb-6 mysurface">
          <v-chip class="" :class="has_info ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-information</v-icon>
            <span> NFO </span>
          </v-chip>

          <v-chip class="" :class="has_poster ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-panorama</v-icon>
            <span> Poster </span>
          </v-chip>

          <v-chip class="" :class="has_subtitle ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-text</v-icon>
            <span> Lyrics </span>
          </v-chip>
          <v-divider></v-divider>
          <v-chip class="" :class="has_audio ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-music-note</v-icon>
            <span> Audio </span>
          </v-chip>

          <v-chip class="" :class="has_video ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-video</v-icon>
            <span> Video </span>
          </v-chip>
          <v-chip class="" :class="has_album_nfo ? 'myprimary' : 'mywarning'">
            <v-icon class="mr-2">mdi-information</v-icon>
            <span> Album NFO </span>
          </v-chip>

          <v-divider></v-divider>

          <v-btn @click="download_video" class="myerror">
            <v-icon>mdi-download</v-icon>
            <span> Download Video (Future) </span>
          </v-btn>
          <v-btn @click="download_info" class="myerror">
            <v-icon>mdi-download</v-icon>
            <span> Download Info (Future) </span>
          </v-btn>

          <v-btn @click="create_album_nfo" class="myerror">
            <v-icon>mdi-download</v-icon>
            <span> Create Jellyfin Info File </span>
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
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
