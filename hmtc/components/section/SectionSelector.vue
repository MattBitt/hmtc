<template>
  <v-card max-width="90%">
    <v-tabs vertical v-model="selected" mandatory color="primary" class="mx-4">
      <v-tab v-for="(section, i) in sections" :key="section.id">
        {{ durationString(section.start) }} - {{ durationString(section.end) }}
      </v-tab>
      <v-tab-item v-for="(section, i) in sections" :key="i">
        <v-container>
          <v-range-slider
            :value="[section.start, section.end]"
            :max="video_duration"
            min="0"
            show-ticks="always"
            tick-size="4"
            readonly
            color="primary"
          >
            <template v-slot:prepend>
              <span class="tracknumber">{{ (i + 1).toString() }}</span>
              <span>({{ section.id }})</span>
            </template>
            <template v-slot:append>
              <h4 class="primary--text font-weight-bold">
                {{ durationString(section.end - section.start) }}
              </h4>
            </template>
          </v-range-slider>
          <v-row>
            <v-col cols="4">
              <v-text-field
                v-model="new_topic"
                label="Create New Topic"
                single-line
                hide-details
                clearable
                @click:clear="clearTopic"
                @keyup.enter="createTopic(new_topic)"
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-row>
                <v-col cols="12">
                  <v-chip-group column multiple>
                    <v-chip
                      v-for="topic in section.topics.slice(0, 9)"
                      close
                      :key="topic.text"
                      color="primary"
                      text-color="white"
                      @click:close="removeTopic(topic.id)"
                    >
                      {{ topic.text }}
                    </v-chip>
                  </v-chip-group>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row justify="start">
            <v-col cols="2">
              <v-btn class="button mywarning" @click="removeSection(section)"
                ><v-icon>mdi-delete</v-icon>Delete</v-btn
              >
            </v-col>
          </v-row>
        </v-container>
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>
<script>
module.exports = {
  name: "Sectionalizer",
  props: {
    sections: {
      type: Array,
      required: true,
    },
    video_duration: {
      type: Number,
      required: true,
    },
  },
  emits: [],
  data() {
    return {
      children: [],
      new_topic: "",
      selected: 0,
    };
  },
  methods: {
    removeSection(section) {
      console.log("removing section", section);
      this.remove_section(section);
    },
    durationString(duration) {
      const durationSeconds = duration / 1000;
      const hrs = ~~(durationSeconds / 3600);
      const mins = ~~((durationSeconds % 3600) / 60);
      const secs = ~~durationSeconds % 60;
      let ret = "";
      if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
      }

      ret += "" + mins + ":" + (secs < 10 ? "0" : "");
      ret += "" + secs;
      // console.log("calculated: ", ret);
      return ret;
    },
    createTopic() {
      const args = {
        section_id: this.sections[this.selected].id,
        topic_string: this.new_topic,
      };
      console.log("Creating New_topic for section", this.args);
      this.create_topic(args);
      this.new_topic = "";
    },
    clearTopic() {
      this.reset();
    },
    removeTopic(topic_id) {
      const args = {
        section_id: this.sections[this.selected].id,
        topic_id: topic_id,
      };
      this.remove_topic(args);
      console.log("Removing topic", args);
    },
  },
  watch: {},
  created() {
    console.log("children: ", this.children);
    // console.log(sections, section, selected);
  },
  computed: {},
};
</script>

<style></style>
