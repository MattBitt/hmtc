<template>
  <v-card tabindex="0" ref="timelineCard" class="timeline-card">
    <div class="timeline-container">
      <v-slider
        v-model="localVideoTime"
        :max="totalDuration"
        :min="0"
        step="0.1"
        @input="onSliderInput"
        class="slider"
        ticks
        hide-details
      ></v-slider>
    </div>

    <div>
      <v-btn @click="markStart" :disabled="isEditingMode" class="mark-button"
        >Mark Start</v-btn
      >
      <v-btn @click="markEnd" :disabled="!isEditingMode" class="mark-button"
        >Mark End</v-btn
      >
    </div>
  </v-card>
</template>

<script>
module.exports = {
  props: {
    totalDuration: {
      type: Number,
      required: true,
    },
    videoTime: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      localVideoTime: this.videoTime,
      isEditingMode: false,
      debounceTimeout: null,
      debounceTime: 100,
      touchDebounceTime: 300,
    };
  },

  watch: {
    videoTime(newValue) {
      this.localVideoTime = newValue;
    },
  },

  computed: {},

  methods: {
    markStart() {
      this.isEditingMode = true;
      console.log("Editing mode enabled. Start time marked at:", this.localVideoTime);
    },

    markEnd() {
      this.isEditingMode = false;
      console.log("End time marked at:", this.localVideoTime);
    },

    onSliderInput(newTime) {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }

      const isTouchEvent = "ontouchstart" in window;

      const debounceDuration = isTouchEvent ? this.touchDebounceTime : this.debounceTime;

      this.debounceTimeout = setTimeout(() => {
        this.localVideoTime = newTime;
        this.update_video_time(newTime);
      }, debounceDuration);
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

.slider {
  margin: 20px 0;
}

.mark-button {
  margin: 5px;
}
</style>
