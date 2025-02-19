<template>
  <div>
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
          <span class="tracknumber">XX</span>
          <span>({{ section.id }})</span>
        </template>
        <template v-slot:append>
          <h4 class="primary--text font-weight-bold">
            {{ durationString(section.end - section.start) }}
          </h4>
        </template>
      </v-range-slider>
    </v-container>
  </div>
</template>
<script>
module.exports = {
  name: "Section Selector",
  props: {
    section: {
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
      new_title: "",
      new_comment: "",
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
