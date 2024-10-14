<template>
  <v-row>
    <v-list-item-group>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title>Section ID: {{ section.id }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title
            >Section Description: {{ section.start }}-{{
              section.end
            }}</v-list-item-title
          >
        </v-list-item-content>
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title
            >Section Topics: ({{ topics.length }})</v-list-item-title
          >
        </v-list-item-content>
      </v-list-item>
    </v-list-item-group>
  </v-row>
</template>
<script>
module.exports = {
  name: "SummaryPanel",
  props: { topics: Array, section: Object },
  data() {
    return {};
  },
  emits: [""],
  methods: {},
};
</script>
