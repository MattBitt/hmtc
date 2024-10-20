<template>
  <v-sheet light>
    <v-form ref="myform" v-model="valid" lazy-validation>
      <v-text-field
        v-model="title"
        :rules="titleRules"
        label="Title"
        required
      ></v-text-field>

      <v-text-field
        v-model="length"
        :rules="lengthRules"
        label="Length"
        required
      ></v-text-field>

      <v-btn :disabled="!valid" color="primary" class="mr-4" @click="validate">
        Submit
      </v-btn>

      <v-btn color="error" class="mr-4" @click="reset"> Reset Form </v-btn>
    </v-form>
  </v-sheet>
</template>
<script>
module.exports = {
  name: "SectionTrackForm",
  props: { section: Object },
  emits: ["saveTrack"],
  data() {
    return {
      valid: false,
      hasAudioFile: false,
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
      this.length = (this.section.end - this.section.start) / 1000;
    },
    resetValidation() {
      this.$refs.myform.resetValidation();
    },
  },
  created() {
    console.log("SectionTrackPanel created", this.section);
    this.length = (this.section.end - this.section.start) / 1000;
  },
  computed: {},
};
</script>
<style></style>
