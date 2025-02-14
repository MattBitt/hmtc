<template>
  <div>
    <v-row>
      <v-col cols="4">
        <v-text-field
          v-model="topic"
          label="Search"
          single-line
          hide-details
          clearable
          @click:clear="clearSearch"
          @keyup.enter="createTopic(topic)"
        ></v-text-field>
      </v-col>
    </v-row>
  </div>
</template>

<script>
module.exports = {
  name: "NewTopic",
  props: {},
  emits: [],
  data() {
    return {
      topic: "",
    };
  },
  watch: {},
  methods: {
    createTopic() {
      this.create(this.topic);
      this.topic = "";
      console.log("Creating Topic", this.topic);
    },
    clearSearch() {
      this.reset();
    },
  },
};
</script>
<style></style>
