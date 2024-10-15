<template>
  <div>
    <v-row class="info--text" justify="end">
      <h6>ID: {{ section.id }}</h6>
    </v-row>

    <v-row>
      <v-range-slider
        :value="readSectionRange"
        :max="barRange.max"
        :min="barRange.min"
        show-ticks="always"
        tick-size="4"
        readonly
      >
        <template v-slot:append>
          <h3>{{ prettyTime(barRange.max) }}</h3>
        </template>
      </v-range-slider>
    </v-row>
    <v-row>
      <v-col cols="8">
        <span class="seven-seg"
          >{{ prettyTime(section.start / 1000) }}-{{
            prettyTime(section.end / 1000)
          }}</span
        >
      </v-col>
      <v-col cols="4">
        <h3>{{ section.section_type }}</h3>
      </v-col>
    </v-row>
    <v-row v-if="topics.length > 0">
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
