<template>
  <v-card>
    <v-row>
      <v-col cols="6">
        <h3>
          <span class="primary--text"
            >{{ section.track.track_number + "." }}
            {{ section.track.title }}</span
          >
        </h3>
        <h4>Files starts here</h4>
        <ul>
          <li v-for="file in section.track.files" :key="file.id">
            <span>{{ file.filename }}</span>
          </li>
        </ul>
        <h4>and ends here</h4>
      </v-col>
      <v-col cols="6">
        <v-btn
          @click="removeTrack(section.id)"
          class="button mywarning"
          outlined
          ><v-icon>mdi-delete</v-icon>Delete Track</v-btn
        >
      </v-col>
    </v-row>
    <v-row justify="end">
      <v-card-actions>
        <div v-if="hasAudioFile">
          <v-btn @click="deleteAudioFile" class="button mywarning" outlined
            ><v-icon>mdi-delete</v-icon>Delete MP3</v-btn
          >
        </div>
        <div v-else>
          <v-btn @click="createAudioFile" color="primary">Create MP3</v-btn>
        </div>
        <div v-if="hasLyrics">
          <v-btn @click="deleteLyricFile" class="button mywarning" outlined
            ><v-icon>mdi-delete</v-icon>Delete Lyrics</v-btn
          >
        </div>
        <div v-else>
          <v-btn @click="createLyricsFile" color="primary">Create Lyrics</v-btn>
        </div>
      </v-card-actions>
    </v-row>
  </v-card>
</template>
<script>
module.exports = {
  name: "SectionTrackPanel",
  props: {
    section: Object,
    hasAudioFile: Boolean,
    hasSubtitle: Boolean,
  },
  emits: [
    "removeTrack",
    "createAudioFile",
    "deleteAudioFile",
    "createLyricsFile",
    "deleteLyricsFile",
  ],
  data() {
    return {
      valid: true,
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
      hasLyrics: false,
    };
  },
  methods: {
    removeTrack(id) {
      this.$emit("removeTrack", id);
      this.hasAudioFile = false;
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
      this.$emit("deleteAudioFile", this.section.track.id);
    },
    createLyricsFile() {
      const args = {
        section_id: this.section.id,
        video_id: this.section.video_id,
        track_id: this.section.track.id,
        title: this.section.track.title,
        length: this.length,
      };
      this.hasLyrics = true;
      console.log("createLyricsFile", args);
      this.$emit("createLyricsFile", args);
    },
    deleteLyricFile() {
      console.log("deleteLyricsFile");
      this.hasLyrics = false;
      this.$emit("deleteLyricsFile", this.section.track.id);
    },
  },
  created() {
    // console.log("SectionTrackPanel created", this.section);
    console.log(this.section.track);
    this.hasAudioFile = this.section.track?.has_mp3;
    this.length = (this.section.end - this.section.start) / 1000;
  },
  computed: {},
};
</script>
<style></style>
