<template>
  <v-container fluid class="" id="tabbed-container">
    <v-tabs v-model="tabs" center-active>
      <v-tab v-for="item in tabItems" :key="item.id"> {{ item.id }} </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tabs">
      <v-tab-item v-for="item in tabItems" :key="item.id">
        <v-container>
          <v-row>
            {{ item.id }} - {{ item.text }} - {{ timeString(item.start) }} -
            {{ timeString(item.end) }}</v-row
          >
          <v-row>
            <v-col cols="4">
              <v-row>
                <v-text-field
                  v-model="topic"
                  :rules="topicRules"
                  label="Enter Topic"
                  required
                  @keydown.enter="
                    handleSubmit(item.id, topic, item.topics.length)
                  "
                ></v-text-field>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <v-btn class="button" block @click="handleCancel">
                    Cancel
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    class="button"
                    block
                    @click="handleSubmit(item.id, topic, item.topics.length)"
                  >
                    Submit
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="4">
              <v-row>
                <v-col
                  v-for="topic in item.topics"
                  :key="topic.text + topic.id"
                >
                  <v-chip
                    :key="topic.id"
                    close
                    @click:close="removeItem(item.id, topic.text)"
                  >
                    {{ topic.text }}</v-chip
                  >
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="4">
              <v-row>
                <v-btn
                  outlined
                  class="mywarning"
                  block
                  @click="removeSection(item.id)"
                >
                  Remove Section
                </v-btn>
              </v-row>
            </v-col>
          </v-row>
          <v-row>
            <v-container id="section-info-container">
              <v-row id="section-times">
                <v-col id="start_time" cols="6">
                  <v-row justify="center" class="mb-6">
                    <span class="seven-seg">{{ timeString(item.start) }}</span>
                  </v-row>

                  <v-row justify="center">
                    <v-col cols="4">
                      <v-btn xs class="button" @click="setStartTime(-0.25)">
                        -0.25
                      </v-btn>
                      <v-btn xs class="button" @click="setStartTime(-1)">
                        -1
                      </v-btn>
                      <v-btn xs class="button" @click="setStartTime(-5)">
                        -5
                      </v-btn>
                    </v-col>
                    <v-col cols="4">
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="loopStartJellyfin()">
                          Play
                        </v-btn>
                      </v-row>
                      <v-row>
                        <v-btn class="button" @click="adjustStartToCurrent()">
                          Sync (jf)
                        </v-btn>
                      </v-row>
                    </v-col>
                    <v-col cols="4">
                      <v-btn xs class="button" @click="setStartTime(+0.25)">
                        +0.25
                      </v-btn>
                      <v-btn xs class="button" @click="setStartTime(+1)">
                        +1
                      </v-btn>
                      <v-btn xs class="button" @click="setStartTime(+5)">
                        +5
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-col>

                <v-col id="end_time" cols="6">
                  <v-row justify="center" class="mb-6">
                    <span class="seven-seg">{{ timeString(item.end) }}</span>
                  </v-row>

                  <v-row justify="center">
                    <v-col cols="4">
                      <v-btn xs class="button" @click="setEndTime(-0.25)">
                        -0.25
                      </v-btn>
                      <v-btn xs class="button" @click="setEndTime(-1)">
                        -1
                      </v-btn>
                      <v-btn xs class="button" @click="setEndTime(-5)">
                        -5
                      </v-btn>
                    </v-col>
                    <v-col cols="4">
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="loopEndJellyfin()">
                          Play
                        </v-btn>
                      </v-row>
                      <v-row>
                        <v-btn class="button" @click="adjustEndToCurrent()">
                          Sync (jf)
                        </v-btn>
                      </v-row>
                    </v-col>
                    <v-col cols="4">
                      <v-btn xs class="button" @click="setEndTime(+0.25)">
                        +0.25
                      </v-btn>
                      <v-btn xs class="button" @click="setEndTime(+1)">
                        +1
                      </v-btn>
                      <v-btn xs class="button" @click="setEndTime(+5)">
                        +5
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-col>
              </v-row>
            </v-container>
          </v-row>
        </v-container>
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
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
    handleSubmit(item_id, topic, num_topics) {
      console.log("Submitted", item_id, topic, "blash");
      this.tabItems
        .filter((item) => item.id === item_id)[0]
        .topics.push({ id: 0, text: topic });
      this.topic = "";
      const args = {
        item_id: item_id,
        topic: topic,
      };
      this.add_item(args);
      // run api call here
    },
    handleCancel() {
      this.topic = "";
      console.log("Cancelled");
    },

    removeItem(item_id, topic) {
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

    timeString(ms) {
      return new Date(ms).toLocaleTimeString();
    },
    setStartTime(value) {
      if (this.editedItem.start + value * 1000 >= 0) {
        this.editedItem.start += value * 1000;
        this.startStringJS = this.timeString(this.editedItem.start);
      }
    },
    setEndTime(value) {
      this.editedItem.end += value * 1000;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
    timeString(value) {
      const date = new Date(null);
      date.setSeconds(value / 1000);
      console.log(date.toISOString().slice(11, 19));
      return date.toISOString().slice(11, 19);
    },
    loopStartJellyfin() {
      this.loop_jellyfin(this.editedItem.start);
    },
    // Jellyfin Looping delay defined below
    loopEndJellyfin() {
      this.loop_jellyfin(this.editedItem.end - 1);
    },

    adjustStartToCurrent() {
      // this doesn't work since current_postion doesn't change
      // need to call it from python
      this.editedItem.start = this.current_position;
      this.startStringJS = this.timeString(this.editedItem.start);
    },

    adjustEndToCurrent() {
      this.editedItem.end = this.current_position;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
  },
};
</script>
