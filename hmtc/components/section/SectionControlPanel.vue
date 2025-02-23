<template>
  <div class="mt-4">
    <v-dialog v-model="dialog" max-width="800px" hide-overlay>
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
          <v-spacer></v-spacer>
          <v-col cols="10">
            <v-col cols="12">
              <span>
                <v-btn class="button" @click="createOneSection"
                  >Whole Thing as 1 Section</v-btn
                >
              </span>
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
            </v-col></v-col
          ><v-spacer></v-spacer>
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
  props: {},

  emits: ["deleteAllSections", "createSection", "startAtJellyfin", "endAtJellyfin"],

  methods: {
    createSection(start, end) {
      // console.log("Creating section", start, end);

      const args = {
        start: start,
        end: end,
      };
      this.create_section(args);
    },

    deleteAllSections() {
      // console.log("Deleting all sections");
      this.delete_all_sections();
    },
    createOneSection() {
      // console.log("Creating a new section");
      this.createSection(0, this.video.duration);
    },
    createEvenSections() {
      // console.log("Creating even sections");
      for (let i = 0; i < this.numEvenSections; i++) {
        this.createSection(i * 180, (i + 1) * 180);
      }
    },
    createStdSectionAt0() {
      console.log("Creating a standard section at 0");
      this.createSection(0, 180);
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
      return Math.floor(this.video.duration / 180); //AVERAGE_SECTION_LENGTH
    },
    enableJellyfin() {
      return this.jellyfin_status.status === "active";
    },
  },
  created() {
    console.log("SectionControlPanel created");
    console.log(this.video);
  },
  data() {
    return {
      jellyfin_status: {},
      video: {},
      dialog: false,
      valid: false,
    };
  },
};
</script>
