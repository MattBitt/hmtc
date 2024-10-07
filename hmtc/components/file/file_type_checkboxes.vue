<template>
  <v-container class="" fluid>
    <p class="myheader">Files</p>
    <v-row class="my-4" justify="center">
      <MyToolTipChip
        icon="mdi-information"
        message="Youtube .info.json"
        :myclass="has_info ? 'myprimary' : 'mywarning'"
      />

      <MyToolTipChip
        icon="mdi-text"
        message="Lyrics"
        :myclass="has_subtitle ? 'myprimary' : 'mywarning'"
        @myclicked="showMessage"
      />
      <MyToolTipChip
        icon="mdi-panorama"
        message="Poster"
        :myclass="has_poster ? 'myprimary' : 'mywarning'"
      />
    </v-row>

    <v-row class="my-4" justify="center">
      <MyToolTipChip
        icon="mdi-music-note"
        message="Audio"
        :myclass="has_audio ? 'myprimary' : 'mywarning'"
      />
      <MyToolTipChip
        icon="mdi-video"
        message="Video"
        :myclass="has_video ? 'myprimary' : 'mywarning'"
        @myclicked="download_video"
      />
      <MyToolTipChip
        icon="mdi-information"
        message="Album NFO"
        :myclass="has_album_nfo ? 'myprimary' : 'mywarning'"
      />
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
  methods: {
    showMessage(message) {
      console.log("Message from child", message);
    },
  },
  mounted() {},
};
</script>

<style>
.myheader {
  font-size: 1em;
  font-weight: bold;
  margin-bottom: 6px;
  text-align: center;
}
</style>
