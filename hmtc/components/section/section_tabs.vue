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
      <v-tab key="main">Main</v-tab>
      <v-tab v-for="(item, index) in tabItems" :key="item.id">
        <span> ({{ item.id }})</span>
        <span>{{ index + 1 }}</span>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tabs">
      <v-tab-item>
        <v-container>
          <h1>
            <v-icon left> mdi-screw-flat-top </v-icon>
            Admin
          </h1>
        </v-container>
      </v-tab-item>
      <v-tab-item v-for="item in tabItems" :key="item.id">
        <v-tabs vertical>
          <v-tab>
            <v-icon left> mdi-clock-digital </v-icon>
            Times
          </v-tab>
          <v-tab>
            <v-icon left> mdi-table-of-contents </v-icon>
            Topics
          </v-tab>
          <v-tab>
            <v-icon left> mdi-music </v-icon>
            Musical Info
          </v-tab>
          <v-tab>
            <v-icon left> mdi-screw-flat-top </v-icon>
            Admin
          </v-tab>

          <v-tab-item>
            <v-container class="px-10">
              <v-row justify="end">
                <v-btn
                  :class="[editingTime ? 'mywarning' : 'myprimary']"
                  @click="toggleEditMode"
                  ><span v-if="editingTime"
                    ><v-icon>mdi-content-save</v-icon></span
                  ><span v-else><v-icon>mdi-pencil</v-icon></span></v-btn
                >
              </v-row>
              <SectionTimePanel
                :initialTime="item.start"
                :isEditing="editingTime"
                @updateTimes="updateTimes"
                @updateSectionTimeFromJellyfin="updateSectionTime"
              />
              <SectionTimePanel
                :initialTime="item.end"
                :isEditing="editingTime"
                @updateTimes="updateTimes"
                @updateSectionTimeFromJellyfin="updateSectionTime"
              />

              <v-row v-if="editingTime" justify="end">
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="updateTimes(item.id, item.start, item.end)"
                >
                  <v-icon> mdi-content-save </v-icon>
                </v-btn>
              </v-row>
            </v-container>
          </v-tab-item>
          <v-tab-item>
            <v-container>
              <SectionTopicsPanel
                :topics="item.topics"
                :item="item"
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
            <SectionAdminPanel @deleteSection="removeSection(item.id)" />
          </v-tab-item>
        </v-tabs>
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
      topic: "",
      valid: false,
      error: "",
      success: "",

      tabItems: [
        {
          id: 1,
          text: "Tab 1",
          start: 0,
          end: 123456,
          topics: [{ id: 1, text: "blue" }],
        },
        ,
      ],
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
      const sectionIndex = this.tabItems.findIndex(
        (item) => item.id === section_id
      );
      if (sectionIndex !== -1) {
        this.tabItems.splice(sectionIndex, 1);
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

    toggleEditMode() {
      if (this.timeFormDirty && this.editingTime) {
        alert("You have unsaved changes");
        //this.timeFormDirty = false;
        return;
      }
      this.editingTime = !this.editingTime;
      console.log("Toggled edit mode", this.editingTime);
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
