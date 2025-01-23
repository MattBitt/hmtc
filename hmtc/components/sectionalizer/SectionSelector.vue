<template>
  <v-card class="mx-auto" max-width="400">
    <h1>{{ selected }}</h1>
    <v-list>
      <v-list-item-group v-model="selected" mandatory color="indigo">
        <v-list-item v-for="(section, i) in sections" :key="i">
          <v-list-item-content>
            <v-list-item-title v-text="section.start_time"></v-list-item-title>
            <v-list-item-title v-text="section.end_time"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-card>
</template>
<script>
module.exports = {
  name: "SectionSelector",
  props: {
    sections: {
      type: Array,
      required: true,
    },
    selected: {
      type: Object,
      required: true,
    },
  },
  emits: [],
  data() {
    return {};
  },
  methods: {
    updateSelected(value) {
      this.set_selected(value);
    },
  },
  watch: {
    selected(newValue) {
      this.updateSelected(newValue);
    },
  },
  created() {},
  computed: {},
};
</script>

<style></style>
