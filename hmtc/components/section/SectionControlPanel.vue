<template>
  <div>
    <v-row justify="space-between">
      <v-col cols="4">
        <v-btn class="button" @click="createOneSection">Create 1 Section</v-btn>
      </v-col>
      <v-col cols="4">
        <v-btn outlined class="button" @click="createEvenSections"
          >Create {{ numEvenSections }} Sections</v-btn
        >
      </v-col>
      <v-col cols="4">
        <v-btn outlined class="button" @click="createStdSectionAt0"
          >Create section at 0</v-btn
        >
      </v-col>
    </v-row>
    <v-row v-if="enableJellyfin" justify="space-between">
      <v-col cols="4">
        <v-btn class="button" @click="startSectionAtJellyfin"
          >Start Section at Jellyfin</v-btn
        >
      </v-col>
      <v-col cols="4">
        <v-btn class="button" @click="endSectionAtJellyfin"
          >End Section at Jellyfin</v-btn
        >
      </v-col>
    </v-row>
    <v-row justify="center">
      <v-col cols="4">
        <v-btn outlined class="button mywarning" @click="deleteAllSections"
          >Delete All Sections</v-btn
        >
      </v-col>
    </v-row>
  </div>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "SectionControlPanel",
  props: { video_duration: Number, jellyfin_status: Object },

  emits: [
    "deleteAllSections",
    "createSection",
    "startAtJellyfin",
    "endAtJellyfin",
  ],

  methods: {
    createSection(start, end) {
      console.log("Creating section", start, end);

      const args = {
        start: start,
        end: end,
      };
      this.create_section(args);
    },

    deleteAllSections() {
      console.log("Deleting all sections");
      this.delete_all_sections();
    },
    createOneSection() {
      console.log("Creating a new section");
      this.createSection(0, this.video_duration);
    },
    createEvenSections() {
      console.log("Creating even sections");
      for (let i = 0; i < this.numEvenSections; i++) {
        this.createSection(i * 300, (i + 1) * 300);
      }
    },
    createStdSectionAt0() {
      console.log("Creating a standard section at 0");
      this.createSection(0, 300);
    },
    startSectionAtJellyfin() {
      console.log("Creating a section at jellyfin time");
      this.$emit("startAtJellyfin");
    },
    endSectionAtJellyfin() {
      console.log("Creating a section at jellyfin time");
      this.$emit("endAtJellyfin");
    },
  },
  computed: {
    numEvenSections() {
      return Math.floor(this.video_duration / 300); //AVERAGE_SECTION_LENGTH
    },
    enableJellyfin() {
      return this.jellyfin_status.status === "active";
    },
  },
  data() {
    return {};
  },
};
</script>
