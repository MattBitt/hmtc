<!-- 10/15/24 Im copying this page into section_carousel  -->

<template>
  <div>
    <v-sheet light>
      <v-row justify="center" class="mb-6">
        <v-range-slider
          :value="sectionRange"
          :max="video_duration"
          min="0"
          show-ticks="always"
          tick-size="4"
          readonly
          color="primary"
        >
          <template v-slot:append>
            <h3 color="info">{{ prettyTime(video_duration) }}</h3>
          </template>
        </v-range-slider>
      </v-row>
    </v-sheet>

    <v-carousel v-model="slides" progress-color="primary" height="500">
      <v-carousel-item
        v-for="(section, index) in sectionItems"
        :key="section.id"
        reverse-transition="fade-transition"
        transition="fade-transition"
      >
        <v-row> </v-row>
        <v-row class="">
          <v-spacer></v-spacer>
          <v-col cols="5">
            <SummaryPanel
              :section="section"
              :topics="section.topics"
              :barRange="{ min: 0, max: this.video_duration }"
              :sectionRange="[section.start / 1000, section.end / 1000]"
            ></SummaryPanel>
          </v-col>
          <v-col cols="5">
            <SectionTrackPanel />
            <v-btn @click="createTrack(section.id)" class="button"
              >Create Track</v-btn
            >
            <v-btn @click="removeTrack(section.id)" class="button"
              >Remove Track</v-btn
            >
          </v-col>
          <v-spacer></v-spacer>
        </v-row>
        <v-row> </v-row>

        <v-row justify="center" class="mt-10">
          <v-dialog
            v-model="dialog[index]"
            fullscreen
            hide-overlay
            transition="dialog-bottom-transition"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn color="primary" dark v-bind="attrs" v-on="on">
                <v-icon>mdi-pencil</v-icon>Edit Section
              </v-btn>
            </template>

            <v-toolbar dark color="primary">
              <v-btn icon dark @click="dialog[index] = false">
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
        </v-row>
      </v-carousel-item>
    </v-carousel>
  </div>
</template>

<script>
export default {
  data() {
    return {
      video_duration: 0,
      dialog: {},
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
    createTrack(section_id) {
      console.log("Creating track", section_id);
      const args = {
        section_id: section_id,
      };
      this.create_track(args);
    },
    removeTrack(section_id) {
      console.log("Removing track", section_id);
      const args = {
        section_id: section_id,
      };
      this.remove_track(args);
    },
    prettyTime(time) {
      return new Date(time * 1000).toISOString().substr(11, 8);
    },
  },
  computed: {
    sectionRange() {
      const selected = this.sectionItems[this.slides];
      return [selected.start / 1000, selected.end / 1000];
    },
  },
};
</script>
<style>
.border4 {
  border: 4px solid var(--primary);
}
</style>
