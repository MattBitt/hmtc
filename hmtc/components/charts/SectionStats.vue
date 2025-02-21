<template>
  <div>
    <v-card>
      <v-row justify="space-between" class="icon-square px-2 mx-1 py-1">
        <v-icon size="30" color="white">{{ icon }}</v-icon>
        <h3>Section Stats (Hours)</h3>
      </v-row>
      <v-col cols="12">
        <v-row justify="space-between">
          <h4>Unique Videos</h4>
          <v-chip color="myprimary">{{ stats.video_hours }}</v-chip>
        </v-row>
        <v-row justify="space-between">
          <h4>Non-Unique Videos</h4>
          <v-chip color="myprimary">{{ stats.non_unique_video_hours }}</v-chip>
        </v-row>

        <v-row justify="space-between">
          <h4>Musical Sections</h4>
          <v-chip color="myprimary">{{ stats.section_hours }}</v-chip>
        </v-row>
        <v-row justify="space-between">
          <h4>Non-Musical Sections</h4>
          <v-chip color="myprimary">{{ stats.non_musical_section_hours }}</v-chip>
        </v-row>
        <v-row justify="space-between">
          <h4>Fine Tuned</h4>
          <v-chip color="myprimary">{{ stats.fine_tuned_section_hours }}</v-chip>
        </v-row>
      </v-col>
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
