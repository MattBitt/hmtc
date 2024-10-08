<template>
  <div>
    <span>Artists Info</span>
    <v-btn class="button" @click="emitMyClicked">Click this button</v-btn>
  </div>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "ArtistsInfo",
  props: { initialName: String, initialURL: String },
  data() {
    return {
      name: this.initialName,
      url: this.initialURL,
    };
  },
  emits: ["myclicked"],
  methods: {
    myclose() {
      alert("Chip close clicked");
    },
    emitMyClicked() {
      console.log("Emitting in Artists Info");
      this.$emit("myclicked", 1);
    },
  },
};
</script>
