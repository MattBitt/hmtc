<template>
  <v-container class="" fluid>
    <p class="myheader">Files</p>
    <v-row class="my-4" justify="center">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            class="mx-2"
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
            class="mx-2"
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
            class="mx-2"
            :class="has_info ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-text</v-icon>
          </v-chip>
        </template>
        <span>Lyrics</span>
      </v-tooltip>
    </v-row>

    <v-row class="my-4" justify="center">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
            class="mx-2"
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
            class="mx-2"
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

    <v-row justify="center">
      <v-btn @click="download_info" class="myprimary">
        <v-icon>mdi-download</v-icon>
        <v-icon>mdi-information</v-icon>
      </v-btn>

      <v-btn @click="download_video" class="myprimary">
        <v-icon>mdi-download</v-icon>
        <v-icon>mdi-video</v-icon>
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
      absolute: true,
      opacity: 1,
      overlay: false,
    };
  },
  methods: {},
  mounted() {},
};
</script>

<style scoped>
.bottom-gradient {
  background-image: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.4) 0%,
    transparent 72px
  );
}

.repeating-gradient {
  background-image: repeating-linear-gradient(
    -45deg,
    rgba(255, 0, 0, 0.25),
    rgba(255, 0, 0, 0.25) 5px,
    rgba(0, 0, 255, 0.25) 5px,
    rgba(0, 0, 255, 0.25) 10px
  );
}
.myheader {
  font-size: 1em;
  font-weight: bold;
  margin-bottom: 6px;
  text-align: center;
}
</style>
