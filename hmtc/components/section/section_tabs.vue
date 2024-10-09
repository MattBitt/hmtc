<template>
  <v-container>
    <v-tabs
      v-model="tabs"
      grow
      show-arrows
      icons-and-text
      next-icon="mdi-arrow-right-bold-box-outline"
      prev-icon="mdi-arrow-left-bold-box-outline"
    >
      <v-tab v-for="(section, index) in sectionItems" :key="section.id">
        <span> ({{ section.id }})</span>
        <span>{{ index + 1 }}</span>
      </v-tab>
      <v-tab key="main">Main</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tabs">
      <v-tab-item v-for="section in sectionItems" :key="section.id">
        <v-tabs vertical>
          <v-tab v-for="sectionTab in sectionTabs" :key="sectionTab.id">
            <v-icon left>{{ sectionTab.icon }} </v-icon>
            {{ sectionTab.text }}
          </v-tab>

          <v-tab-item>
            <v-container class="px-10">
              <SectionTimePanel
                :initialTime="section.start"
                :isEditing="editingTime"
                @updateTimes="updateTimes"
                @updateSectionTimeFromJellyfin="updateSectionTime"
              />
              <SectionTimePanel
                :initialTime="section.end"
                :isEditing="editingTime"
                @updateTimes="updateTimes"
                @updateSectionTimeFromJellyfin="updateSectionTime"
              />

              <v-row v-if="editingTime" justify="end">
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="updateTimes(section.id, section.start, section.end)"
                >
                  <v-icon> mdi-content-save </v-icon>
                </v-btn>
              </v-row>
            </v-container>
          </v-tab-item>

          <v-tab-item>
            <v-container>
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
      </v-tab-item>
      <v-tab-item>
        <v-container>
          <h1>
            <v-icon left> mdi-screw-flat-top </v-icon>
            <SectionControlPanel :video_duration="video_duration" />
          </h1>
        </v-container>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      editingTime: false,
      timeFormDirty: false,
      tabs: 0,
      sectionTabs: [
        { text: "Times", icon: "mdi-clock-digital" },
        { text: "Topics", icon: "mdi-table-of-contents" },
        { text: "Musical Info", icon: "mdi-music" },
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

    loopJellyfinAt(value) {
      console.log("Looping Jellyfin at", value, this.jellyfin_status);
      this.loop_jellyfin(value);
    },

    updateTimes(item_id, start, end) {
      console.log("Updating times", item_id, start, end);
      const args = {
        item_id: item_id,
        start: start,
        end: end,
      };
      this.update_times(args);
      this.editingTime = false;
      this.timeFormDirty = false;
    },
  },
};
</script>
<style></style>
