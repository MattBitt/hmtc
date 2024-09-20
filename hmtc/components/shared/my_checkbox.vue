<template>
  <v-container class="px-0" fluid>
    <v-row align-content="center">
      <v-col>
        <v-checkbox v-model="has_audio" label="audio"></v-checkbox>
      </v-col>
      <v-col>
        <v-checkbox v-model="has_video" label="video"></v-checkbox>
      </v-col>
      <v-col>
        <v-checkbox v-model="has_info" label="info"></v-checkbox>
      </v-col>
      <v-col>
        <v-checkbox v-model="has_poster" label="poster"></v-checkbox>
      </v-col>
      <v-col>
        <v-checkbox v-model="has_subtitle" label="subtitle"></v-checkbox>
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
};
</script>
<style></style>
