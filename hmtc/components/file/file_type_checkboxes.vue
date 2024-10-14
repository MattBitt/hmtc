<template>
  <v-row class="" justify="center">
    <v-col cols="10">
      <v-row class="ml-2 mt-1">
        <MyToolTipChip
          icon="mdi-information"
          message="Youtube .info.json"
          :color="has_info ? 'primary' : 'warning'"
          @myclicked="download_info"
        />

        <MyToolTipChip
          icon="mdi-text"
          message="Lyrics"
          :color="has_subtitle ? 'primary' : 'warning'"
          @myclicked="download_info"
        />
        <MyToolTipChip
          icon="mdi-panorama"
          message="Poster"
          :color="has_poster ? 'primary' : 'warning'"
          @myclicked="download_info"
        />

        <MyToolTipChip
          icon="mdi-music-note"
          message="Audio"
          :color="has_audio ? 'primary' : 'warning'"
          @myclicked="download_video"
        />
        <MyToolTipChip
          icon="mdi-video"
          message="Video"
          :color="has_video ? 'primary' : 'warning'"
          @myclicked="download_video"
        />
        <MyToolTipChip
          icon="mdi-information"
          message="Album NFO"
          :color="has_album_nfo ? 'primary' : 'warning'"
          @myclicked="create_album_nfo"
        />
      </v-row>
    </v-col>
    <v-col class="px-0 mx-0 mt-1">
      <VideoFilesInfoModal
        :folder_files="folder_files"
        :db_files="db_files"
      ></VideoFilesInfoModal>
    </v-col>
  </v-row>
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

<style></style>
