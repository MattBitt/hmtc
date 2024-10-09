<template>
  <div>
    <v-btn outlined class="button mywarning" block @click="createOneSection"
      >Delete Section</v-btn
    >
    <v-btn outlined class="button mywarning" block @click="createEvenSections"
      >Delete Section</v-btn
    >
    <v-btn outlined class="button mywarning" block @click="createStdSectionAt0"
      >Delete Section</v-btn
    >
  </div>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "SectionControlPanel",
  props: { video_duration: Number },
  data() {
    return {
      name: this.initialName,
    };
  },
  emits: ["deleteAllSections", "createSection"],
  methods: {
    deleteAllSections() {
      console.log("Deleting all sections");
      this.$emit("deleteAllSections", 1);
    },
    createOneSection() {
      console.log("Creating a new section");
      this.$emit("createSection", 0, this.video_duration);
    },
    createEvenSections() {
      console.log("Creating even sections");
      //this.$emit("createSection", 0, this.video_duration);
    },
    createStdSectionAt0() {
      console.log("Creating a standard section at 0");
      //this.$emit("createSection", 0, this.video_duration);
    },
  },
};
</script>
