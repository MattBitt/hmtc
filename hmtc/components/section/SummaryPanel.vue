<template>
  <div class="mx-6">
    <v-row class="info--text" justify="end">
      <h6>ID: {{ section.id }}</h6>
    </v-row>

    <v-row justify="center" class="mb-6">
      <h2>
        <span class="primary--text"
          ><strong>{{ prettyTime(section.start / 1000) }}</strong>
        </span>
      </h2>
      <h2>-</h2>
      <h2>
        <span class="primary--text"
          ><strong>{{ prettyTime(section.end / 1000) }}</strong></span
        >
      </h2>
    </v-row>
    <v-row justify="center" class="mb-6">
      <h3>{{ section.section_type }}</h3>
    </v-row>
    <v-row v-if="topics.length > 0" justify="center" class="mb-6">
      <v-chip color="info" v-for="topic in topics" :key="topic.id">{{
        topic.text
      }}</v-chip>
    </v-row>
  </div>
</template>
<script>
module.exports = {
  name: "SummaryPanel",
  props: {
    topics: Array,
    section: Object,
    barRange: Object,
    sectionRange: Array,
  },
  data() {
    return {};
  },
  emits: [""],
  methods: {
    prettyTime(time) {
      return new Date(time * 1000).toISOString().substr(11, 8);
    },
  },
  computed: {
    readSectionRange() {
      return this.sectionRange;
    },
  },
};
</script>
<style>
.border1 {
  border: 1px solid black;
}
</style>
