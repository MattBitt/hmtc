<template>
  <div class="mt-4">
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          class="button"
          v-bind="attrs"
          v-on="on"
          :disabled="video.album.title == ''"
        >
          <v-icon>mdi-rhombus-split</v-icon>Sections
        </v-btn>
      </template>
      <v-toolbar dark color="primary">
        <v-btn icon dark @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
        <v-toolbar-title>Sections Editor</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn dark text :disabled="!valid" @click=""> Save </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card>
        <v-row>
          <v-btn class="button" @click="createOneSection"
            >Whole Thing as 1 Section</v-btn
          >

          <v-btn
            outlined
            class="button"
            @click="createEvenSections"
            :disabled="!(numEvenSections > 0)"
          >
            {{ numEvenSections }}
          </v-btn>

          <v-btn outlined class="button" @click="createStdSectionAt0">
            5 minute section at 0</v-btn
          >
          <v-btn outlined class="button" @click="">
            5 minute section after the last one</v-btn
          >

          <v-btn outlined class="button mywarning" @click="deleteAllSections"
            >Delete All Sections</v-btn
          >
        </v-row>
        <h1>{{ video.album?.title }}</h1>
        <v-divider></v-divider>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "SectionControlPanel",
  props: { video: Object, jellyfin_status: Object },

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
      this.createSection(0, this.video.duration);
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
      return Math.floor(this.video.duration / 300); //AVERAGE_SECTION_LENGTH
    },
    enableJellyfin() {
      return this.jellyfin_status.status === "active";
    },
  },
  data() {
    return {
      dialog: false,
      valid: false,
    };
  },
};
</script>
