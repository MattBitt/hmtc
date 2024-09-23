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
          <v-divider></v-divider>
          <v-chip class="myerror mt-10">
            <v-icon @click="download_video">mdi-download</v-icon>
            <span> Download Video (Future) </span>
          </v-chip>
          <v-chip class="myerror">
            <v-icon @click="download_info">mdi-download</v-icon>
            <span> Download Info (Future) </span>
          </v-chip>
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
