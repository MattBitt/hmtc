<template>
  <v-row id="file-statuses" class="mt-2 mb-2">
    <v-col>
      <v-chip class="my-2" :class="has_info ? 'myprimary' : 'mywarning'">
        <v-icon class="mr-2">mdi-information</v-icon>
        <span> NFO </span>
      </v-chip>

      <v-chip class="my-2" :class="has_poster ? 'myprimary' : 'mywarning'">
        <v-icon class="mr-2">mdi-panorama</v-icon>
        <span> Poster </span>
      </v-chip>

      <v-chip class="my-2" :class="has_subtitle ? 'myprimary' : 'mywarning'">
        <v-icon class="mr-2">mdi-text</v-icon>
        <span> Lyrics </span>
      </v-chip>

      <v-chip class="my-2 mr-8" :class="has_audio ? 'myprimary' : 'mywarning'">
        <v-icon class="mr-2">mdi-music-note</v-icon>
        <span> Audio </span>
      </v-chip>

      <v-chip class="my-2 mr-2" :class="has_video ? 'myprimary' : 'mywarning'">
        <v-icon class="mr-2">mdi-video</v-icon>
        <span> Video </span>
      </v-chip>
      <v-divider class="my-4"></v-divider>
      <v-chip class="myprimary-invert">
        <v-icon @click="download_video">mdi-download</v-icon>
        <span> Video </span>
      </v-chip>
      <v-chip class="myprimary-invert">
        <v-icon @click="download_info">mdi-download</v-icon>
        <span> Info </span>
      </v-chip>
    </v-col>
  </v-row>
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
