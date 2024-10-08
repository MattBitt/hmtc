<template>
  <v-row>
    <v-btn outlined class="button mywarning" block @click="emitDeleteSection"
      >Delete Section</v-btn
    >
  </v-row>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "SectionAdminPanel",
  props: { initialName: String },
  data() {
    return {
      name: this.initialName,
    };
  },
  emits: ["deleteSection"],
  methods: {
    emitDeleteSection() {
      console.log("Emitting in Section Admin");
      this.$emit("deleteSection", 1);
    },
  },
};
</script>
