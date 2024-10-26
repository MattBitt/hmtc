<template>
  <v-sheet light>
    <v-form ref="myform" v-model="valid" lazy-validation>
      <v-text-field
        v-model="title"
        :rules="titleRules"
        label="Title"
        required
      ></v-text-field>

      <v-btn :disabled="!valid" color="primary" class="mr-4" @click="validate">
        Create Track
      </v-btn>
    </v-form>
  </v-sheet>
</template>
<script>
module.exports = {
  name: "SectionTrackForm",
  props: { section: Object, defaultTrackTitle: String },
  emits: ["saveTrack"],
  data() {
    return {
      valid: false,
      title: "",
      titleRules: [(v) => !!v || "Title is required"],
      length: 0,
      lengthRules: [
        (v) => !!v || "Length is required",
        (v) => v > 0 || "Length must be valid",
      ],
      select: null,
      items: ["Item 1", "Item 2", "Item 3", "Item 4"],
      checkbox: false,
    };
  },
  methods: {
    validate() {
      this.$refs.myform.validate();
      this.$emit("saveTrack", {
        section_id: this.section.id,
        title: this.title,
        length: this.length,
      });
    },
    reset() {
      this.$refs.myform.reset();
    },
    resetValidation() {
      this.$refs.myform.resetValidation();
    },
  },
  created() {
    console.log("SectionTrackPanel created", this.section);
    this.length = (this.section.end - this.section.start) / 1000;
    console.log("Default TrackTitle", this.defaultTrackTitle);
    this.title = this.defaultTrackTitle;
  },
  computed: {},
};
</script>
<style></style>
