<template>
  <v-card max-width="90%">
    <h1>{{ selected }}</h1>
    <v-tabs vertical v-model="selected" mandatory color="primary" class="mx-4">
      <v-tab v-for="(section, i) in sections" :key="i">
        {{ durationString(section.start) }} - {{ durationString(section.end) }}
      </v-tab>
      <v-tab-item v-for="(section, i) in sections" :key="i">
        <v-row justify="center">
          <jupyter-widget
            v-if="children.length > 0"
            :widget="children[0]"
            key="first-widget"
          ></jupyter-widget>
        </v-row>
        <v-row>
          <jupyter-widget
            v-if="children.length > 1"
            :widget="children[1]"
            key="videoframe-widget"
          ></jupyter-widget>
          <jupyter-widget
            v-if="children.length > 2"
            :widget="children[2]"
            key="subtitles-widget"
          ></jupyter-widget>
        </v-row>
        <v-card>
          <v-card-text
            ><h3>Some text for {{ section }}</h3>
            <h3>{{ i }}: section index</h3>
          </v-card-text>
        </v-card>
        <v-container>
          <v-range-slider
            :value="[section.start, section.end]"
            :max="video_time"
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
          <v-row justify="center">
            <v-col cols="2">
              <h4 class="primary--text font-weight-bold">
                {{ durationString(section.end - section.start) }}
              </h4>
            </v-col>
            <v-col cols="8">
              <h4 class="primary--text font-weight-bold">
                {{ section.topics?.map(({ text }) => text).join(", ") }}
              </h4>
            </v-col>
          </v-row>
        </v-container>
      </v-tab-item>
    </v-tabs>
  </v-card>
</template>
<script>
module.exports = {
  name: "SectionSelector",
  props: {
    sections: {
      type: Array,
      required: true,
    },
    selected: {
      type: Object,
      required: true,
    },
    video_time: {
      type: Number,
      required: true,
    },
  },
  emits: [],
  data() {
    return {
      children: [],
    };
  },
  methods: {
    updateSelected(value) {
      this.set_selected(value);
      console.log("Updating to ", value);
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
      console.log("calculated: ", ret);
      return ret;
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
