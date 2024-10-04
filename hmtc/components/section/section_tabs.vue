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
      <v-tab v-for="(item, index) in tabItems" :key="item.id">
        <span> ({{ item.id }})</span>
        <span>{{ index + 1 }}</span>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tabs">
      <v-tab-item v-for="item in tabItems" :key="item.id">
        <v-tabs vertical>
          <v-tab>
            <v-icon left> mdi-lock </v-icon>
            Timing
          </v-tab>
          <v-tab>
            <v-icon left> mdi-account </v-icon>
            Topics
          </v-tab>
          <v-tab>
            <v-icon left> mdi-access-point </v-icon>
            Beat/ <br />
            Artists
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
              <!-- Start Time Control Panel -->
              <v-row justify="center" class="mb-6">
                <span class="seven-seg myprimary">{{
                  timeString(item.start)
                }}</span>
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="updateSectionTime(item.id, 'start')"
                >
                  <v-icon>mdi-sync</v-icon>
                </v-btn>
              </v-row>
              <v-row v-if="editingTime" justify="center" class="mt-4">
                <v-btn medium fab class="" @click="item.start += -5000">
                  <v-icon>mdi-rewind-5</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.start += -1000">
                  <v-icon>mdi-rewind</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.start += -250">
                  <v-icon>mdi-step-backward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.start += 250">
                  <v-icon>mdi-step-forward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.start += 1000">
                  <v-icon>mdi-fast-forward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.start += 5000">
                  <v-icon>mdi-fast-forward-5</v-icon>
                </v-btn>
              </v-row>
              <v-row justify="center">
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="loopJellyfinAt(item.start)"
                >
                  <v-icon> mdi-play </v-icon>
                </v-btn>
              </v-row>
              <!-- End Time Control Panel -->
              <v-row justify="center" class="mt-5 mb-5">
                <span class="seven-seg myprimary">{{
                  timeString(item.end)
                }}</span>
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="updateSectionTime(item.id, 'end')"
                >
                  <v-icon>mdi-sync</v-icon>
                </v-btn>
              </v-row>
              <v-row v-if="editingTime" justify="center" class="mt-4">
                <v-btn medium fab class="" @click="item.end += -5000">
                  <v-icon>mdi-rewind-5</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.end += -1000">
                  <v-icon>mdi-rewind</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.end += -250">
                  <v-icon>mdi-step-backward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.end += 250">
                  <v-icon>mdi-step-forward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.end += 1000">
                  <v-icon>mdi-fast-forward</v-icon>
                </v-btn>
                <v-btn medium fab class="" @click="item.end += 5000">
                  <v-icon>mdi-fast-forward-5</v-icon>
                </v-btn>
              </v-row>
              <v-row justify="center">
                <v-btn
                  x-large
                  fab
                  class="button"
                  @click="loopJellyfinAt(item.end)"
                >
                  <v-icon> mdi-play </v-icon>
                </v-btn>
              </v-row>
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
              <v-row class="px-10" align-items="center">
                <v-spacer></v-spacer>
                <v-col cols="6">
                  <v-text-field
                    v-model="topic"
                    :rules="topicRules"
                    label="Enter Topic"
                    required
                    @keydown.enter="
                      handleSubmitTopic(item.id, topic, item.topics.length)
                    "
                  ></v-text-field>
                </v-col>
                <v-col cols="3">
                  <v-btn
                    class="button"
                    block
                    @click="
                      handleSubmitTopic(item.id, topic, item.topics.length)
                    "
                  >
                    Submit
                  </v-btn>
                </v-col>
                <v-spacer></v-spacer>
              </v-row>

              <v-row class="mt-10 ml-6">
                <v-col
                  v-for="topic in item.topics"
                  :key="topic.text + topic.id"
                >
                  <v-chip
                    :key="topic.id"
                    close
                    @click:close="removeTopic(item.id, topic.text)"
                  >
                    {{ topic.text }}</v-chip
                  >
                </v-col>
              </v-row>
            </v-container>
          </v-tab-item>
          <v-tab-item>
            <v-container> Beats/Artists Tab</v-container>
          </v-tab-item>

          <v-tab-item>
            <v-container>
              <v-row justify="center">
                <v-col cols="6">
                  <v-btn
                    outlined
                    class="button mywarning"
                    block
                    @click="removeSection(item.id)"
                  >
                    Remove Section
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
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
      // i think in order to use the following, i need to use the
      // on-blur events
      // topicRules: [(v) => !!v || "Topic is required"],
      topicRules: [],
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
    handleSubmitTopic(item_id, topic, num_topics) {
      console.log("Submitted Topic", item_id, topic);
      this.tabItems
        .filter((item) => item.id === item_id)[0]
        .topics.push({ id: 0, text: topic });
      this.topic = "";
      const args = {
        item_id: item_id,
        topic: topic,
      };
      // python function
      this.add_item(args);
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

    removeTopic(item_id, topic) {
      console.log("Removing topic", item_id, topic);
      const item = this.tabItems.filter((item) => item.id === item_id)[0];
      const topicIndex = item.topics.findIndex((t) => t.text === topic);
      if (topicIndex !== -1) {
        item.topics.splice(topicIndex, 1);
      }

      const args = {
        item_id: item_id,
        topic: topic,
      };
      // python function
      this.remove_item(args);
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

    timeString(value) {
      return new Date(value).toISOString().slice(11, 19);
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
