<template>
  <div class="mt-4">
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn class="button" v-bind="attrs" v-on="on">
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
          <v-col cols="3">
            <v-btn class="button" @click="createOneSection">Whole</v-btn>
          </v-col>
          <v-col cols="3">
            <v-btn
              outlined
              class="button"
              @click="createEvenSections"
              :disabled="!(numEvenSections > 0)"
            >
              {{ numEvenSections }}
            </v-btn>
          </v-col>
          <v-col cols="3">
            <v-btn outlined class="button" @click="createStdSectionAt0">
              at 0</v-btn
            >
          </v-col>
          <v-col cols="3">
            <v-btn outlined class="button mywarning" @click="deleteAllSections"
              >Delete All Sections</v-btn
            >
          </v-col>
        </v-row>
        <v-row v-if="enableJellyfin" justify="space-between">
          <v-col cols="3">
            <v-btn class="button" @click="startSectionAtJellyfin"
              >Start Section at Jellyfin</v-btn
            >
          </v-col>
          <v-col cols="3">
            <v-btn class="button" @click="endSectionAtJellyfin"
              >End Section at Jellyfin</v-btn
            >
          </v-col>
        </v-row>
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
    return {
      dialog: false,
      valid: false,
    };
  },
};
</script>
