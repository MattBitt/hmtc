<template>
  <v-container>
    <v-row>
      <v-col cols="4">
        <v-row>
          <h1>{{ section_id }}</h1>
        </v-row>
        <v-row>
          <v-form ref="form" v-model="valid" @submit.prevent="handleSubmit">
            <v-text-field
              v-model="topic"
              :rules="topicRules"
              label="Enter Topic"
              required
            ></v-text-field>
            <v-btn type="submit" color="primary">Submit</v-btn>
          </v-form>
        </v-row>
        <v-row class="mt-6">
          <v-alert outlined v-if="error" type="error" dismissible>{{
            error
          }}</v-alert>
          <v-alert outlined v-if="success" type="success" dismissible>{{
            success
          }}</v-alert>
        </v-row>
      </v-col>
      <v-col cols="8">
        <v-chip
          v-for="sectionTopic in section_topics"
          :key="sectionTopic.id"
          class="mx-4"
          close
          @click:close="deleteSectionTopic(sectionTopic)"
        >
          {{ sectionTopic.text }}
        </v-chip>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
module.exports = {
  topic: "",
  section_topics: ["kiwi"],
  valid: false,
  success: "",
  error: "",
  // topicRules: [(v) => !!v || "Topic is required"],
  topicRules: [],

  methods: {
    async handleSubmit() {
      this.error = "";
      this.success = "";
      if (this.$refs.form.validate()) {
        try {
          // this topic already exists with this section. give error that
          // duplicates are not allowed
          const topicExistsInSection = await this.section_topics.includes(
            this.topic
          );

          console.log(
            "Topic exists in section:",
            topicExistsInSection,
            this.section_topics
          );
          if (!topicExistsInSection) {
            // need to query the database to see if the topic exists
            try {
              await this.add_topic(this.topic);
              this.section_topics.push(this.topic);
              this.success = "Topic added successfully.";
              this.topic = "";
            } catch (err) {
              this.error = "An error occurred while adding the topic." + err;
              this.topic = "";
            }
          } else {
            this.error = "This topic already exists in this section.";
            this.topic = "";
          }
          this.topic = "";
        } catch (err) {
          this.error = "An error occurred while processing your request." + err;
          this.topic = "";
        }
      }
    },
    async deleteSectionTopic(topic) {
      console.log("Deleting topic from this section:", topic);
      this.section_topics = this.section_topics.filter((t) => t !== topic);
      this.remove_topic(topic);
      // Replace with actual API call to delete a section topic entry
      // Example:
      // await axios.delete(`/api/sectiontopics/${topic}`);
    },
  },
};
</script>

<style scoped id="section_topics_css">
.v-container {
  width: 100%;
}
</style>
