<template>
  <div class="mx-6">
    <v-row class="info--text" justify="end">
      <h6>ID: {{ section.id }}</h6>
    </v-row>
    <v-sheet light>
      <v-row justify="center" class="mb-6">
        <v-range-slider
          :value="readSectionRange"
          :max="barRange.max"
          :min="barRange.min"
          show-ticks="always"
          tick-size="4"
          readonly
          color="primary"
        >
          <template v-slot:append>
            <h3 color="info">{{ prettyTime(barRange.max) }}</h3>
          </template>
        </v-range-slider>
      </v-row>
    </v-sheet>
    <v-row justify="center" class="mb-6">
      <span class="seven-seg">{{ prettyTime(section.start / 1000) }} </span>
      <h1>-</h1>
      <span class="seven-seg">{{ prettyTime(section.end / 1000) }}</span>
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
