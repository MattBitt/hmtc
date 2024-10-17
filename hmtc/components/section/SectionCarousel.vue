<!-- 10/15/24 Im copying this page into section_carousel  -->

<template>
  <div>
    <v-carousel v-model="slides" progress-color="primary">
      <v-carousel-item
        v-for="(section, index) in sectionItems"
        max-height="300"
        :key="section.id"
      >
        <v-sheet light class="mx-4">
          <div class="text-center">
            <SummaryPanel
              :section="section"
              :topics="section.topics"
              :barRange="{ min: 0, max: video_duration }"
              :sectionRange="[section.start / 1000, section.end / 1000]"
            ></SummaryPanel>
            <v-row justify="center">
              <h1>Section {{ index + 1 }} {{ section.id }}</h1>
            </v-row>

            <v-dialog
              v-model="dialog"
              fullscreen
              hide-overlay
              transition="dialog-bottom-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn color="primary" dark v-bind="attrs" v-on="on">
                  Click Me
                </v-btn>
              </template>

              <v-toolbar dark color="primary">
                <v-btn icon dark @click="dialog = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title>Section {{ index + 1 }}</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-toolbar-items>
                  <v-btn dark text :disabled="!valid" @click=""> Save </v-btn>
                </v-toolbar-items>
              </v-toolbar>
              <v-card>
                <v-card-title class="text-h5 grey lighten-2">
                  Privacy Policy ()
                  {{ section.id }}
                  {{ section.start }}
                  {{ section.end }}
                </v-card-title>

                <v-card-text>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
                  do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                  Ut enim ad minim veniam, quis nostrud exercitation ullamco
                  laboris nisi ut aliquip ex ea commodo consequat. Duis aute
                  irure dolor in reprehenderit in voluptate velit esse cillum
                  dolore eu fugiat nulla pariatur. Excepteur sint occaecat
                  cupidatat non proident, sunt in culpa qui officia deserunt
                  mollit anim id est laborum.
                </v-card-text>
                <v-container class="px-10">
                  <v-divider></v-divider>
                  <SectionTimePanel
                    :sectionID="section.id"
                    :video_duration="video_duration"
                    :initialTime="section.start"
                    @updateTime="updateSectionStart"
                    @updateSectionTimeFromJellyfin="updateSectionTime"
                    @loopJellyfin="loopJellyfinAtStart"
                  />
                  <SectionTimePanel
                    :sectionID="section.id"
                    :video_duration="video_duration"
                    :initialTime="section.end"
                    @updateTime="updateSectionEnd"
                    @updateSectionTimeFromJellyfin="updateSectionTime"
                    @loopJellyfin="loopJellyfinAtEnd"
                  />
                </v-container>
                <v-divider></v-divider>
                <v-container>
                  <!-- i think the :topics below is incorrect 10/9/24 -->
                  <SectionTopicsPanel
                    :topics="section.topics"
                    :item="section"
                    @addTopic="addTopic"
                    @removeTopic="removeTopic"
                  />
                </v-container>
                <v-divider></v-divider>
                <v-container>
                  <BeatsInfo />
                  <ArtistsInfo />
                </v-container>
                <v-divider></v-divider>
                <SectionAdminPanel @deleteSection="removeSection(section.id)" />
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="primary" text @click="dialog = false">
                    I accept
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </div>
        </v-sheet>
      </v-carousel-item>
    </v-carousel>
  </div>
</template>

<script>
export default {
  data() {
    return {
      video_duration: 0,
      dialog: false,
      slides: 0,
      valid: true,
    };
  },
  methods: {
    addTopic(args) {
      this.add_item(args);
    },

    removeTopic(args) {
      this.remove_item(args);
    },

    createSectionAtJellyfin(start_or_end) {
      console.log("Creating section at jellyfin", start_or_end);
      const args = {
        start_or_end: start_or_end,
      };
      this.create_section_from_jellyfin(args);
    },

    updateSectionTime(section, start_or_end) {
      console.log("Updating times", section, start_or_end);
      const args = {
        section: section,
        start_or_end: start_or_end,
      };
      // python function
      this.update_section_from_jellyfin(args);
    },

    removeSection(section_id) {
      console.log("Removing section", section_id);
      const sectionIndex = this.sectionItems.findIndex(
        (item) => item.id === section_id
      );
      if (sectionIndex !== -1) {
        this.sectionItems.splice(sectionIndex, 1);
      }
      const args = {
        section_id: section_id,
      };
      this.delete_section(args);
    },

    loopJellyfinAtStart(value) {
      this.loop_jellyfin(value);
    },
    loopJellyfinAtEnd(value) {
      this.loop_jellyfin(value);
    },

    updateSectionStart(section_id, new_time) {
      console.log("Updating times", section_id);
      const args = {
        item_id: section_id,
        start: new_time,
      };
      console.log("Args", args);
      this.update_times(args);
    },
    updateSectionEnd(section_id, new_time) {
      console.log("Updating times", section_id);
      const args = {
        item_id: section_id,
        end: new_time,
      };
      this.update_times(args);
    },
  },
};
</script>
<style></style>
