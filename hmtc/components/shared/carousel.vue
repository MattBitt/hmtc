<template>
  <v-container fluid class="" id="carousel-container">
    <v-card>
      <v-tabs v-model="tab" centered>
        <v-tabs-slider></v-tabs-slider>
        <v-tab
          v-for="(section, i) in sections"
          :key="i"
          :value="'tab-' + i"
          :href="'#tab-' + i"
        >
          <h3>{{ i + 1 }}</h3>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item
          v-for="(section, i) in sections"
          :key="i"
          :value="'tab-' + i"
        >
          <v-card flat>
            <v-card-text>{{ text }}</v-card-text>
            <v-sheet class="mt-4" height="100%">
              <v-container>
                <v-row>
                  <v-col cols="4">
                    <v-row>
                      <h1>{{ section.id }}</h1>
                    </v-row>
                    <v-row>
                      <v-form
                        ref="form"
                        v-model="valid"
                        @submit.prevent="handleSubmit"
                      >
                        <v-text-field
                          v-model="topic"
                          :rules="topicRules"
                          label="Enter Topic"
                          required
                        ></v-text-field>
                        <v-btn type="submit" color="primary">Submit</v-btn>
                      </v-form>
                    </v-row>
                    <v-row class="mt-6">
                      <v-alert outlined v-if="error" type="error" dismissible>{{
                        error
                      }}</v-alert>
                      <v-alert
                        outlined
                        v-if="success"
                        type="success"
                        dismissible
                        >{{ success }}</v-alert
                      >
                    </v-row>
                  </v-col>
                  <v-col cols="8">
                    <v-chip
                      v-for="sectionTopic in section_topics"
                      :key="sectionTopic.id"
                      class="mx-4"
                      close
                      @click:close="deleteSectionTopic(sectionTopic)"
                    >
                      {{ sectionTopic.text }}
                    </v-chip>
                  </v-col>
                </v-row>
              </v-container>
              <container id="section-info-container">
                <v-row id="section-times">
                  <v-col id="start_time" cols="6">
                    <v-row justify="center" class="mb-6">
                      <span class="seven-seg">{{
                        timeString(section.start)
                      }}</span>
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
                      <span class="seven-seg">{{
                        timeString(section.end)
                      }}</span>
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
              </container>
            </v-sheet>
          </v-card>
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      tab: null,
      text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      timeline: {
        whole_start: 0,
        whole_end: 300,
        part_start: 60,
        part_end: 240,
        section_number: 1,
        total_sections: 5,
        thumbColor: "teal",
      },
      section_item: {
        section_type: "INITIAL",
        start: 0,
        end: 0,
        id: 682148,
      },
      section: null,
      section_topics: [
        {
          id: 1,
          text: "Topic 1",
        },
        {
          id: 2,
          text: "Topic 2",
        },
        {
          id: 3,
          text: "Topic 3",
        },
      ],
      model: 0,
      topic: "",
      valid: false,
      success: "",
      error: "",
      // i think in order to use the following, i need to use the
      // on-blur events
      // topicRules: [(v) => !!v || "Topic is required"],
      topicRules: [],
    };
  },

  methods: {
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
    async handleSubmit() {
      this.error = "";
      this.success = "";
      if (this.$refs.form.validate()) {
        try {
          // this topic already exists with this section. give error that
          // duplicates are not allowed
          const topicExistsInSection = await this.section_topics.includes(
            this.topic
          );

          console.log(
            "Topic exists in section:",
            topicExistsInSection,
            this.section_topics
          );
          if (!topicExistsInSection) {
            // need to query the database to see if the topic exists
            try {
              await this.add_topic(this.topic);
              this.section_topics.push(this.topic);
              this.success = "Topic added successfully.";
              this.topic = "";
            } catch (err) {
              this.error = "An error occurred while adding the topic." + err;
              this.topic = "";
            }
          } else {
            this.error = "This topic already exists in this section.";
            this.topic = "";
          }
          this.topic = "";
        } catch (err) {
          this.error = "An error occurred while processing your request." + err;
          this.topic = "";
        }
      }
    },
    async deleteSectionTopic(topic) {
      console.log("Deleting topic from this section:", topic);
      this.section_topics = this.section_topics.filter((t) => t !== topic);
      this.remove_topic(topic);
      // Replace with actual API call to delete a section topic entry
      // Example:
      // await axios.delete(`/api/sectiontopics/${topic}`);
    },
  },
};
</script>
<style id="slider-css">
/* persistant hint of slider */
.v-messages__message {
  text-align: center;
  font-size: 20px;

  color: var(--on-primary);
}

.seven-seg {
  font-family: "mySevenSegDisplay";
  font-size: 3em;
  color: var(--primary) !important;
  margin: 10px;
}
</style>
