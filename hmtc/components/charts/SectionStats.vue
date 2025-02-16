<template>
  <div>
    <v-card>
      <v-row justify="space-between" class="icon-square px-2 mx-1 py-1">
        <v-icon size="30" color="white">{{ icon }}</v-icon>
        <h3>Section Stats (Hours)</h3>
      </v-row>
      <v-row justify="center">
        <v-col cols="8">
          <v-row justify="space-between">
            <h4>Videos</h4>
            <v-chip color="myprimary">{{ stats.video_hours }}</v-chip>
          </v-row>
          <v-row justify="space-between">
            <h4>Sections</h4>
            <v-chip color="myprimary">{{ stats.section_hours }}</v-chip>
          </v-row>
          <v-row justify="space-between">
            <h4>Fine Tuned</h4>
            <v-chip color="myprimary">{{ stats.fine_tuned_section_hours }}</v-chip>
          </v-row>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
module.exports = {
  name: "DomainCard",
  props: { title: String, icon: String, stats: Object },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {},
  computed: {},
};
</script>
<style>
.icon-square {
  justify-content: center;
  align-items: center;
  background-color: var(--primary);
  color: white;
}
</style>
