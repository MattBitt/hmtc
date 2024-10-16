<template>
  <v-tooltip bottom>
    <template v-slot:activator="{ on, attrs }">
      <v-chip class="mx-8" v-bind="attrs" v-on="on">
        <!-- <v-icon class="">mdi-music-note</v-icon>
        <p>{{ message }}</p> -->
        <ANewComponent :message="message" />
      </v-chip>
    </template>
    <span>This is the tooltip for {{ message }} does this also reload</span>
  </v-tooltip>
</template>

<script>
module.exports = {
  name: "ChildComponent",
  props: {
    message: {
      type: String,
      required: true,
    },
  },
};
</script>

<style>
p {
  color: blue;
}
</style>
