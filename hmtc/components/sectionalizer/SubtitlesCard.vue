<template>
  <v-card max-width="40%">
    <v-row class="info--text>" justify="end">
      <h6>Hello World</h6>
      <h2>{{ video_time }}</h2>
      <h4>{{ someprop }}</h4>
    </v-row>
  </v-card>
</template>

<script>
module.exports = {
  name: "SubtitlesCard",
  props: {
    video_time: {
      type: Number,
      required: true,
    },
  },
  emits: [],
  data() {
    return {
      someprop: "asdf",
    };
  },
  methods: {},
  created() {},
  computed: {},
};
</script>
<style></style>
