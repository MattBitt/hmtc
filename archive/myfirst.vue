<template>
  <v-card-text>
    <v-container>
      <v-row>
        <v-col cols="12" sm="6" md="4">
          <v-text-field
            :value="title"
            v-model="title"
            label="Title"
          ></v-text-field>
        </v-col>
        <v-col cols="12" sm="6" md="4">
          <v-text-field
            :value="releaseDate"
            v-model="releaseDate"
            label="Release Date"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-btn @click="$emit('myincrease', title, releaseDate)">Click Me</v-btn>
      </v-row>
    </v-container>
  </v-card-text>
</template>
<script>
// i created this to start exploring vue components
// inheritence and how to pass data between them
module.exports = {
  name: "MyFirst",
  props: { initialTitle: String, initialReleaseDate: String },
  data() {
    return {
      title: this.initialTitle,
      releaseDate: this.initialReleaseDate,
    };
  },
  emits: ["myincrease"],
  methods: {
    myclose() {
      alert("Chip close clicked");
    },
    increaseInParent() {
      console.log("Emitting in Child", this.title, this.releaseDate);
      this.$emit("myincrease", 1);
    },
  },
};
</script>
