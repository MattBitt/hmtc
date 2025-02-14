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
          </v-row>
          <v-row justify="center">
            <v-col cols="2">
              <h4 class="primary--text font-weight-bold">
                {{ durationString(section.end - section.start) }}
              </h4>
            </v-col>
            <v-col cols="6">
              <h4 class="primary--text font-weight-bold">
                {{ section.topics?.map(({ text }) => text).join(", ") }}
              </h4>
            </v-col>
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
    selected: {
      type: Object,
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
    };
  },
  methods: {
    updateSelected(value) {
      this.update_selected(value);
      console.log("Updating to ", value);
    },
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
      this.create_topic(this.new_topic);
      this.new_topic = "";
      console.log("Creating New_topic", this.new_topic);
    },
    clearTopic() {
      this.reset();
    },
  },
  watch: {
    selected(newValue) {
      this.updateSelected(newValue);
    },
  },
  created() {
    console.log("children: ", this.children);
    // console.log(sections, section, selected);
  },
  computed: {},
};
</script>

<style></style>
