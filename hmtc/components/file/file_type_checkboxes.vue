<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="mt-2 mb-2"><h2>Files</h2></div>
      </v-col>
      <v-col cols="8">
        <div class="mt-2 mb-2 mychecks">
          <v-icon>mdi-download</v-icon>
          <span v-if="has_info">
            <s> NFO </s>
          </span>

          <span v-else> NFO </span>
        </div>

        <div class="mt-2 mb-2 mychecks">
          <v-icon>mdi-panorama</v-icon>
          <span v-if="has_poster">
            <s> Poster </s>
          </span>
          <span v-else> Poster </span>
        </div>

        <div class="mt-2 mb-2 mychecks">
          <v-icon>mdi-text</v-icon>
          <span v-if="has_subtitle">
            <s>Lyrics</s>
          </span>
          <span v-else> Lyrics </span>
        </div>
      </v-col>
      <v-col cols="4">
        <div>
          <v-icon>mdi-download</v-icon>
        </div>
      </v-col>
      <v-col cols="8">
        <div class="mt-10 mb-2 mychecks">
          <v-icon>mdi-music-note</v-icon>
          <span v-if="has_audio">
            <s> .MP3 </s>
          </span>
          <span v-else> .MP3 </span>
        </div>

        <div class="mt-2 mb-2 mychecks">
          <v-icon>mdi-video</v-icon>
          <span v-if="has_video">
            <s> .MKV </s>
          </span>

          <span v-else> .MKV </span>
        </div>
      </v-col>
      <v-col cols="4">
        <div class="mt-10">
          <v-icon @click="download_video">mdi-download</v-icon>
        </div>
      </v-col>
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
