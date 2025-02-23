<template>
  <div>
    <v-card>
      <v-row justify="space-between" class="icon-square px-2 mx-1 py-1">
        <v-icon size="30" color="white">{{ icon }}</v-icon>
        <h3>Section Stats (Hours)</h3>
      </v-row>
      <v-col cols="12">
        <v-row justify="space-between">
          <h4>Videos</h4>
          <v-chip color="myprimary">Unique {{ stats.video_hours }}</v-chip>
          <v-chip color="myprimary">Non-Unique {{ stats.non_unique_video_hours }}</v-chip>
          <v-chip color="myprimary"
            >Total {{ stats.video_hours + stats.non_unique_video_hours }}</v-chip
          >
        </v-row>

        <v-row justify="space-between">
          <h4>Analyzed</h4>
          <v-chip color="myprimary">Music {{ stats.section_hours }}</v-chip>
          <v-chip color="myprimary"
            >Non Music {{ stats.non_musical_section_hours }}</v-chip
          >
          <v-chip color="myprimary"
            >Total
            {{
              Math.round(
                ((stats.section_hours + stats.non_musical_section_hours) /
                  stats.video_hours) *
                  100 *
                  100
              ) / 100
            }}%</v-chip
          >
        </v-row>
        <v-row justify="space-between">
          <h4>Fine Tuned</h4>
          <v-chip color="myprimary"
            >{{ stats.fine_tuned_section_hours }} ({{
              Math.round(
                (stats.fine_tuned_section_hours / stats.section_hours) * 100 * 100
              ) / 100
            }}%)</v-chip
          >
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
