<!-- 10/15/24 Im copying this page into section_carousel  -->

<template>
  <v-carousel v-model="slides" progress-color="primary" height="300">
    <v-carousel-item v-for="(section, index) in sectionItems" :key="section.id">
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
          <v-row justify="center" class="mt-10">
            <v-btn color="primary" dark v-bind="attrs" v-on="on">
              <v-icon>mdi-pencil</v-icon>Edit Section
            </v-btn>
          </v-row>
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
          <v-container class="px-10">
            <v-card-title>Start Time</v-card-title>
            <SectionTimePanel
              :sectionID="section.id"
              :video_duration="video_duration"
              :initialTime="section.start"
              @updateTime="updateSectionStart"
              @updateSectionTimeFromJellyfin="updateSectionTime"
              @loopJellyfin="loopJellyfinAtStart"
            />
            <v-divider></v-divider>
            <v-card-title>End Time</v-card-title>
            <SectionTimePanel
              :sectionID="section.id"
              :video_duration="video_duration"
              :initialTime="section.end"
              @updateTime="updateSectionEnd"
              @updateSectionTimeFromJellyfin="updateSectionTime"
              @loopJellyfin="loopJellyfinAtEnd"
            />

            <v-divider></v-divider>
            <v-card-title>Topics</v-card-title>

            <!-- i think the :topics below is incorrect 10/9/24 -->
            <SectionTopicsPanel
              :topics="section.topics"
              :item="section"
              @addTopic="addTopic"
              @removeTopic="removeTopic"
            />

            <v-divider></v-divider>
            <v-card-title>Musical</v-card-title>
            <BeatsInfo />
            <ArtistsInfo />

            <v-divider></v-divider>
            <v-card-title>Admin</v-card-title>
            <SectionAdminPanel @deleteSection="removeSection(section.id)" />
          </v-container>
        </v-card>
      </v-dialog>
    </v-carousel-item>
  </v-carousel>
</template>

<script>
export default {
  data() {
    return {
      video_duration: 0,
      dialog: false,
      slides: 0,
      // no form implemented yet
      valid: false,
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
