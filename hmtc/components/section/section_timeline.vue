<template>
  <v-container fluid class="" id="timeline-container">
    <v-row>
      <h1>asdf</h1>
      <v-btn class="button mx-2" @click="prev_slide">Previous</v-btn>

      <v-range-slider
        :value="[part_start, part_end]"
        :min="whole_start"
        :max="whole_end"
        tick-size="4"
        thumb-label="always"
        readonly
        :color="thumbColor"
        :thumb-color="thumbColor"
        :track-color="thumbColor"
        :hint="'Section ' + this.section_number + ' of ' + this.total_sections"
        persistent-hint
      >
      </v-range-slider>

      <v-btn class="button mx-2" @click="next_slide">Next</v-btn>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      whole_start: 0,
      whole_end: 300,
      part_start: 60,
      part_end: 240,
      section_number: 1,
      total_sections: 5,

      thumbColor: "teal",
    };
  },

  methods: {},
};
</script>
<style>
/* persistant hint of slider */
.v-messages__message {
  text-align: center;
  font-size: 20px;

  color: var(--on-primary);
}
</style>
