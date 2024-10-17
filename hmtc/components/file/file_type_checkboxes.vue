<template>
  <div class="text-center">
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" dark v-bind="attrs" v-on="on"> Click Me </v-btn>
      </template>

      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Video Files
        </v-card-title>

        <v-card-text>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
          culpa qui officia deserunt mollit anim id est laborum.
        </v-card-text>

        <v-divider></v-divider>
        <v-card-text>
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
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false"> I accept </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
module.exports = {
  name: "VideoFilesDialog",
  props: {},
  emits: [],
  data() {
    return {
      dialog: false,
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
  methods: {},
  created() {},
  computed: {},

  methods: {
    showMessage(message) {
      console.log("Message from child", message);
    },
  },
  mounted() {},
};
</script>

<style></style>
