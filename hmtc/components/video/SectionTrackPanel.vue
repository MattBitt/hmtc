<template>
  <v-sheet light>
    <v-row>
      <h1>{{ section.track.track_number + ". " }}</h1>
      <h1>{{ section.track.title }}</h1>
      <h1>ID: {{ section.track.id }}</h1>
    </v-row>
    <v-row>
      <v-btn @click="removeTrack(section.id)" class="button"
        >Delete Track</v-btn
      >
    </v-row>
    <v-row>
      <div v-if="hasAudioFile">
        <v-btn @click="deleteAudioFile" color="warning">Delete File</v-btn>
      </div>
      <div v-else>
        <v-btn @click="createAudioFile" color="primary">Create File</v-btn>
      </div>
    </v-row>
  </v-sheet>
</template>
<script>
module.exports = {
  name: "SectionTrackPanel",
  props: { section: Object },
  emits: ["removeTrack", "createAudioFile"],
  data() {
    return {
      valid: true,
      hasAudioFile: false,
      title: "",
      titleRules: [(v) => !!v || "Title is required"],
      length: 0,
      lengthRules: [
        (v) => !!v || "Length is required",
        (v) => v > 0 || "Length must be valid",
      ],
      select: null,
      items: ["Item 1", "Item 2", "Item 3", "Item 4"],
      checkbox: false,
    };
  },
  methods: {
    removeTrack(id) {
      this.$emit("removeTrack", id);
    },
    createAudioFile() {
      this.hasAudioFile = true;
      const args = {
        section_id: this.section.id,
        video_id: this.section.video_id,
        track_id: this.section.track.id,
        title: this.section.track.title,
        length: this.length,
      };
      console.log("createAudioFile", args);
      this.$emit("createAudioFile", args);
    },
    deleteAudioFile() {
      this.hasAudioFile = false;
    },
  },
  created() {
    console.log("SectionTrackPanel created", this.section);

    this.length = (this.section.end - this.section.start) / 1000;
  },
  computed: {},
};
</script>
<style></style>
