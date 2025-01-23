<template>
  <v-card max-width="90%">
    <h1>{{ selected }}</h1>
    <v-tabs vertical v-model="selected" mandatory color="primary">
      <v-tab v-for="(section, i) in sections" :key="i">
        {{ section.start_time }} - {{ section.end_time }}
      </v-tab>
      <v-tab-item v-for="(section, i) in sections" :key="i">
        <v-card>
          <v-card-text
            ><h3>Some text for {{ section }}</h3>
            <h3>{{ i }}: section index</h3>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
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
      console.log("Updating to ", value);
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
