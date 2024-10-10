<template>
  <div>
    <v-row class="px-10" align-items="center">
      <v-spacer></v-spacer>
      <v-col cols="6">
        <v-text-field
          v-model="topic"
          :rules="topicRules"
          label="Enter Topic"
          required
          @keydown.enter="handleSubmitTopic(item.id, topic, item.topics.length)"
        ></v-text-field>
      </v-col>
      <v-col cols="3">
        <v-btn
          class="button"
          block
          @click="handleSubmitTopic(item.id, topic, item.topics.length)"
        >
          Submit
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
    </v-row>

    <v-row class="mt-10 ml-6">
      <v-col v-for="topic in item.topics" :key="topic.text + topic.id">
        <v-chip
          :key="topic.id"
          close
          @click:close="removeTopic(item.id, topic.text)"
        >
          {{ topic.text }}</v-chip
        >
      </v-col>
    </v-row>
  </div>
</template>
<script>
module.exports = {
  name: "SectionTopicsPanel",
  props: { topics: Array, item: Object },
  emits: ["addTopic", "removeTopic"],

  methods: {
    handleSubmitTopic(item_id, topic, num_topics) {
      console.log("Submitted Topic", item_id, topic);
      this.topics.push({ id: 0, text: topic });
      this.topic = "";
      const args = {
        item_id: item_id,
        topic: topic,
      };
      // python function
      this.$emit("addTopic", args);
    },

    removeTopic(item_id, topic) {
      console.log("Removing topic", item_id, topic);
      const topicIndex = this.topics.findIndex((t) => t.text === topic);
      if (topicIndex !== -1) {
        this.topics.splice(topicIndex, 1);
      }

      const args = {
        item_id: item_id,
        topic: topic,
      };
      // python function
      this.$emit("removeTopic", args);
    },
  },
  data() {
    return {
      topic: "",
      // i think in order to use the following, i need to use the
      // on-blur events
      // topicRules: [(v) => !!v || "Topic is required"],
      topicRules: [],
    };
  },
};
</script>
