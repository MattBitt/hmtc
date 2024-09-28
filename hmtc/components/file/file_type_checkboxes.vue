<template>
  <v-container class="" fluid>
    <!-- <template>
      <v-hover>
        <template v-slot:default="{ hover }">
          <v-card class="mx-auto" max-width="344">
            <v-card-text>
              <h2 class="text-h6 primary--text">Magento Forests</h2>
              Travel to the best outdoor experience on planet Earth. A vacation
              you will never forget!
            </v-card-text>

            <v-card-title>
              <v-rating
                :value="4"
                dense
                color="orange"
                background-color="orange"
                hover
                class="mr-2"
              ></v-rating>
              <span class="primary--text text-subtitle-2">64 Reviews</span>
            </v-card-title>

            <v-fade-transition>
              <v-overlay v-if="hover" absolute color="#036358">
                <v-btn>See more info</v-btn>
              </v-overlay>
            </v-fade-transition>
          </v-card>
        </template>
      </v-hover>
    </template> -->

    <v-row justify="space-between" class="mx-2">
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
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
            :class="has_info ? 'myprimary' : 'mywarning'"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon class="">mdi-text</v-icon>
          </v-chip>
        </template>
        <span>Lyrics</span>
      </v-tooltip>

      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-chip
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
    <v-row>
      <v-col cols="4" v-if="!has_video">
        <v-btn outlined @click="download_video" class="myprimary">
          <v-icon>mdi-download</v-icon>
          <span>Video</span>
        </v-btn>
      </v-col>
      <v-col cols="4" v-else>
        <span>Already Downloaded</span>
      </v-col>
      <v-col cols="4" v-if="!has_video">
        <v-btn outlined @click="download_info" class="mywarning">
          <v-icon>mdi-download</v-icon>
          <span> Info</span>
        </v-btn>
      </v-col>
      <v-col cols="4" v-else><span>Already Downloaded</span></v-col>
      <v-col cols="4" v-if="!has_album_nfo">
        <v-btn outlined @click="create_album_nfo" class="myprimary">
          <v-icon>mdi-hammer-wrench</v-icon>
          <span> NFO </span>
        </v-btn>
      </v-col>
      <v-col cols="4" v-else>
        <span>Already Downloaded</span>
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
<style>
.mychecks {
  font-size: 1.4em;
  font-weight: 900;
  margin: 10px 10px 0px 0px;
}
</style>
