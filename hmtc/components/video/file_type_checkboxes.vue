<template>
  <div class="mt-4">
    <v-dialog v-model="dialog" max-width="800px" hide-overlay>
      <template v-slot:activator="{ on, attrs }">
        <v-badge :value="!has_audio" color="warning" overlap>
          <v-btn class="button" v-bind="attrs" v-on="on">
            <v-icon>mdi-folder</v-icon> Files
          </v-btn>
        </v-badge>
      </template>
      <v-toolbar dark color="primary">
        <v-btn icon dark @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>Video Files</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn dark text :disabled="!valid" @click=""> Save </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card>
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
      valid: false,
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
