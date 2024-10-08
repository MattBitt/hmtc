<template>
  <div>
    <span>Beats Info</span>
    <v-btn class="button" @click="emitMyClicked">Click this button</v-btn>
  </div>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "BeatsInfo",
  props: { initialName: String },
  data() {
    return {
      name: this.initialName,
    };
  },
  emits: ["myclicked"],
  methods: {
    myclose() {
      alert("Chip close clicked");
    },
    emitMyClicked() {
      console.log("Emitting in Beats Info");
      this.$emit("myclicked", 1);
    },
  },
};
</script>
