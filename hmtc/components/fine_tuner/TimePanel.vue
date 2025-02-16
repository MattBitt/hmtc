<template>
  <div>
    <v-row justify="center" class="mb-6">
      <span class="seven-seg myprimary">{{ formattedTime }}</span>
    </v-row>
    <v-row justify="center" class="mb-6">
      <v-col cols="3">
        <v-btn fab class="button" @click="toggleEditMode" v-if="!isEditing">
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
        <v-btn fab class="mywarning" @click="toggleEditMode" v-else>
          <v-icon>mdi-cancel</v-icon>
        </v-btn>
      </v-col>
      <v-col cols="3">
        <v-btn fab class="button" @click="loopJellyfinAt">
          <v-icon> mdi-play </v-icon>
        </v-btn>
      </v-col>

      <v-col v-if="isDirty" cols="3">
        <v-btn fab class="button" @click="updateTime">
          <v-icon> mdi-content-save </v-icon>
        </v-btn>
      </v-col>
      <v-col v-else cols="3">
        <div></div>
      </v-col>
    </v-row>

    <v-row v-if="isEditing" justify="center" class="mt-4">
      <v-btn x-small fab class="button" @click="adjustTime(-30_000)">
        <v-icon>mdi-rewind-30</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(-5000)">
        <v-icon>mdi-rewind-5</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(-1000)">
        <v-icon>mdi-rewind</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(-250)">
        <v-icon>mdi-step-backward</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(250)">
        <v-icon>mdi-step-forward</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(1000)">
        <v-icon>mdi-fast-forward</v-icon>
      </v-btn>
      <v-btn small fab class="button" @click="adjustTime(5000)">
        <v-icon>mdi-fast-forward-5</v-icon>
      </v-btn>

      <v-btn x-small fab class="button" @click="adjustTime(30_000)">
        <v-icon>mdi-fast-forward-30</v-icon>
      </v-btn>
    </v-row>
  </div>
</template>

<script>
module.exports = {
  name: "SectionTimePanel",
  props: { video_duration: Number, initialTime: Number },
  emits: [],
  methods: {
    updateTime() {
      const args = {
        time: this.localTime,
      };
      this.update_time(args);
      this.isEditing = false;
      this.isDirty = false;
    },

    toggleEditMode() {
      if (this.isEditing) {
        if (this.isDirty) {
          this.localTime = this.initialTime;
          this.isDirty = false;
        }
      }
      this.isEditing = !this.isEditing;
    },

    loopJellyfinAt() {
      this.loop_jellyfin_at(this.localTime);
    },

    adjustTime(value) {
      const tmp_time = this.localTime + value;
      const durationMS = this.video_duration * 1000;
      console.log(`Attempting to adjust time by ${value} milliseconds.`);
      console.log(`Current time: ${this.localTime} milliseconds.`);
      console.log(`Duration: ${durationMS} milliseconds.`);
      if (tmp_time < 0) {
        this.localTime = 0;
      } else if (tmp_time > durationMS) {
        this.localTime = durationMS;
      } else {
        this.localTime = tmp_time;
      }
      this.isDirty = true;
    },

    formatTime(milliseconds) {
      const seconds = milliseconds / 1000;
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
        2,
        "0"
      )}:${String(secs).padStart(2, "0")}`;
    },
  },
  computed: {
    formattedTime() {
      return this.formatTime(this.localTime);
    },
  },
  created() {
    this.localTime = this.initialTime;
    console.log(`${this.video_duration} is the duration upon creation`);
  },

  data() {
    return {
      localTime: this.initialTime,
      isEditing: false,
      isDirty: false,
    };
  },

  watch: {
    localTime(newVal) {
      // You can keep this if you want to track changes without console logs
    },
  },
};
</script>
