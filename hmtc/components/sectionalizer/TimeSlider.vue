<template>
  <v-card tabindex="0" ref="timelineCard" class="timeline-card mt-10">
    <div class="timeline-container">
      <v-slider
        v-model="localTimeCursor"
        thumb-label="always"
        thumb-size="48"
        :max="totalDuration"
        :min="0"
        step="1"
        @input="onSliderInput"
        class="slider"
      >
        <template v-slot:append>
          <span>{{ durationString }}</span>
        </template>
        <template v-slot:thumb-label>
          <span>{{ formattedTime }}</span>
        </template>
      </v-slider>
    </div>

    <v-row>
      <!-- Removed all button controls -->
    </v-row>
  </v-card>
</template>

<script>
export default {
  props: {
    totalDuration: {
      type: Number,
      required: true,
    },
    durationString: {
      type: String,
      required: true,
    },
    timeCursor: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      localTimeCursor: this.timeCursor,
      isEditingMode: false,
      startTime: null,
      debounceTimeout: null,
      debounceTime: 100,
      touchDebounceTime: 300,
    };
  },

  watch: {
    timeCursor(newValue) {
      console.log("updating to ", newValue);
      this.localTimeCursor = newValue;
    },
  },
  created() {
    console.log("Total duration:", this.totalDuration);
  },

  computed: {
    formattedTime() {
      const totalSeconds = this.localTimeCursor;
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;

      if (hours > 0) {
        return `${hours}:${minutes < 10 ? "0" : ""}${minutes}:${
          seconds < 10 ? "0" : ""
        }${seconds}`;
      } else {
        return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
      }
    },
  },

  methods: {
    markStart() {
      this.isEditingMode = true;
      this.startTime = this.localTimeCursor;
      console.log("Start time marked at:", this.startTime);
    },

    markEnd() {
      this.isEditingMode = false;
      const endTime = this.localTimeCursor;
      console.log("End time marked at:", endTime);

      this.create_section({ start: this.startTime, end: endTime });
    },

    cancelMarkStart() {
      this.isEditingMode = false;
    },

    onSliderInput(newTime) {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }

      const isTouchEvent = "ontouchstart" in window;

      const debounceDuration = isTouchEvent ? this.touchDebounceTime : this.debounceTime;

      this.debounceTimeout = setTimeout(() => {
        this.localTimeCursor = newTime;
        this.update_time_cursor(newTime);
      }, debounceDuration);
    },
    canMarkEnd() {
      const enabled = this.isEditingMode && this.localTimeCursor - this.startTime > 5;
      return enabled;
    },
    adjustTime(delta) {
      this.onSliderInput(this.localTimeCursor + delta);
    },
  },
};
</script>

<style scoped>
.timeline-card {
  outline: none;
}

.timeline-container {
  user-select: none;
  touch-action: none;
  position: relative;
}
</style>
