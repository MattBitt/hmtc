<!-- 10/15/24 Im copying this page into section_carousel  -->

<template>
  <div>
    <v-sheet>
      <SectionControlPanel
        :video_duration="video_duration"
        :jellyfin_status="jellyfin_status"
        @deleteAllSections="deleteSections"
        @createSection="createSection"
        @startAtJellyfin="createSectionAtJellyfin('start')"
        @endAtJellyfin="createSectionAtJellyfin('end')"
      />
    </v-sheet>
    <v-carousel v-model="tabs" progress-color="primary">
      <v-carousel-item
        v-for="(section, index) in sectionItems"
        max-height="400"
        :key="section.id"
      >
        <v-sheet light class="mx-4">
          <v-tabs light class="mb-10">
            <v-tab v-for="sectionTab in sectionTabHeaders" :key="sectionTab.id">
              <span>
                <v-icon>{{ sectionTab.icon }} </v-icon>

                {{ sectionTab.text }}
              </span>
            </v-tab>

            <v-tab-item>
              <v-sheet light tile>
                <SummaryPanel
                  :section="section"
                  :topics="section.topics"
                  :barRange="{ min: 0, max: video_duration }"
                  :sectionRange="[section.start / 1000, section.end / 1000]"
                ></SummaryPanel>
              </v-sheet>
            </v-tab-item>
            <v-tab-item>
              <v-container class="px-10">
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
            </v-tab-item>

            <v-tab-item>
              <v-container>
                <!-- i think the :topics below is incorrect 10/9/24 -->
                <SectionTopicsPanel
                  :topics="section.topics"
                  :item="section"
                  @addTopic="addTopic"
                  @removeTopic="removeTopic"
                />
              </v-container>
            </v-tab-item>

            <v-tab-item>
              <v-container>
                <BeatsInfo />
                <ArtistsInfo />
              </v-container>
            </v-tab-item>

            <v-tab-item>
              <SectionAdminPanel @deleteSection="removeSection(section.id)" />
            </v-tab-item>
          </v-tabs>

          <v-col class="pa-2 mt-auto">
            <h1>Section {{ index + 1 }} {{ section.id }}</h1>
          </v-col>
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
      jellyfin_status: {},

      tabs: 0,
      sectionTabHeaders: [
        { text: "Summary", icon: "mdi-sigma" },
        { text: "Times", icon: "mdi-clock-digital" },
        { text: "Topics", icon: "mdi-table-of-contents" },
        { text: "Musical", icon: "mdi-music" },
        { text: "Admin", icon: "mdi-screw-flat-top" },
      ],
      video_duration: 0,
    };
  },
  methods: {
    addTopic(args) {
      this.add_item(args);
    },

    removeTopic(args) {
      this.remove_item(args);
    },

    createSection(start, end) {
      console.log("Creating section", start, end);

      const args = {
        start: start,
        end: end,
      };
      this.create_section(args);
    },
    createSectionAtJellyfin(start_or_end) {
      console.log("Creating section at jellyfin", start_or_end);
      const args = {
        start_or_end: start_or_end,
      };
      this.create_section_from_jellyfin(args);
    },

    deleteSections() {
      console.log("Deleting all sections");
      this.delete_all_sections();
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
