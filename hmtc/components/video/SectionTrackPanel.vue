<template>
  <v-card>
    <v-row>
      <v-col cols="6">
        <h3>
          <span class="primary--text"
            >{{ track.track_number + "." }} {{ track.title }}</span
          >
        </h3>
        <h4>hasMp3 {{ checkFilesExist().audio }}</h4>
        <h4>hasLyrics {{ checkFilesExist().lyrics }}</h4>
        <h4><strong>Files</strong></h4>
        <ul>
          <li v-for="file in track.files" :key="file.id">
            <span>{{ file.filename }}</span>
            <span>{{ file.file_type }}</span>
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
        <div v-if="hasMp3()">
          <v-btn @click="deleteAudioFile" class="button mywarning" outlined
            ><v-icon>mdi-delete</v-icon>Delete MP3</v-btn
          >
        </div>
        <div v-else>
          <v-btn @click="createAudioFile" color="primary">Create MP3</v-btn>
        </div>
        <div v-if="hasLyrics()">
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
    track: Object,
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
    };
  },
  methods: {
    removeTrack(id) {
      this.$emit("removeTrack", id);
    },
    createAudioFile() {
      const args = {
        section_id: this.section.id,
        video_id: this.section.video_id,
        track_id: this.track.id,
        title: this.track.title,
        length: this.length,
      };
      this.$emit("createAudioFile", args);
    },
    deleteAudioFile() {
      this.$emit("deleteAudioFile", this.track.id);
    },
    createLyricsFile() {
      const args = {
        section_id: this.section.id,
        video_id: this.section.video_id,
        track_id: this.track.id,
        title: this.track.title,
        length: this.length,
      };
      this.$emit("createLyricsFile", args);
    },
    deleteLyricFile() {
      this.$emit("deleteLyricsFile", this.track.id);
    },
    checkFilesExist() {
      _has_audio = this.track.files.some((file) => file.file_type === "audio");
      _has_lyrics = this.track.files.some(
        (file) => file.file_type === "lyrics"
      );

      return { audio: _has_audio, lyrics: _has_lyrics };
    },
    hasMp3() {
      return this.checkFilesExist().audio;
    },
    hasLyrics() {
      return this.checkFilesExist().lyrics;
    },
  },
  computed: {},
  created() {
    this.length = (this.section.end - this.section.start) / 1000;
  },
  computed: {},
};
</script>
<style></style>
