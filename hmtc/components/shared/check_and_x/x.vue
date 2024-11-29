<template>
  <span>
    <v-chip
      v-if="clickable"
      :color="icon_color"
      class="white--text"
      @click="clickHandler"
    >
      <v-icon>mdi-close</v-icon>
    </v-chip>
    <v-chip v-else :color="icon_color" class="white--text">
      <v-icon>mdi-close</v-icon>
    </v-chip>
  </span>
</template>
<script>
module.exports = {
  name: "CheckComponent",
  props: {
    clickable: Boolean,
    icon_color: String,
  },
  emits: [],
  data() {
    return {};
  },
  methods: {
    clickHandler() {
      this.click();
    },
  },
};
</script>
