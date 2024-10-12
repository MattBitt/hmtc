<template>
  <v-container class="" fluid>
    <v-row class="mx-0" justify="center">
      <MyToolTipChip
        icon="mdi-information"
        message="Youtube .info.json"
        :myclass="has_info ? 'myprimary' : 'mywarning'"
        @myclicked="download_info"
      />

      <MyToolTipChip
        icon="mdi-text"
        message="Lyrics"
        :myclass="has_subtitle ? 'myprimary' : 'mywarning'"
        @myclicked="download_info"
      />
      <MyToolTipChip
        icon="mdi-panorama"
        message="Poster"
        :myclass="has_poster ? 'myprimary' : 'mywarning'"
        @myclicked="download_info"
      />

      <MyToolTipChip
        icon="mdi-music-note"
        message="Audio"
        :myclass="has_audio ? 'myprimary' : 'mywarning'"
        @myclicked="download_video"
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
        @myclicked="create_album_nfo"
      />

      <VideoFilesInfoModal
        :folder_files="folder_files"
        :db_files="db_files"
      ></VideoFilesInfoModal>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      db_files: [],
      folder_files: [],
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
