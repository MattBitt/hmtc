<template>
  <v-card tabindex="0" ref="timelineCard" class="timeline-card">
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
      <v-col cols="5">
        <v-row justify="center">
          <span v-if="isEditingMode">
            <v-btn @click="cancelMarkStart" class="button mywarning">Cancel</v-btn>
            <span>Section started at {{ startTime }}</span>
          </span>
          <span v-else>
            <v-btn @click="markStart" class="button">Mark Start</v-btn>
          </span>
          <v-btn @click="markEnd" :disabled="!canMarkEnd()" class="button"
            >Mark End</v-btn
          >
        </v-row>
      </v-col>
      <v-col cols="2">
        <span class="seven-seg">{{ timeCursor }}</span>
      </v-col>
      <v-col v-if="totalDuration < 300" cols="5">
        <v-row justify="end">
          <v-btn medium fab class="button" @click="adjustTime(-5)">
            <v-icon>mdi-rewind-5</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(-1)">
            <v-icon>mdi-rewind</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(1)">
            <v-icon>mdi-fast-forward</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(5)">
            <v-icon>mdi-fast-forward-5</v-icon>
          </v-btn>
        </v-row>
      </v-col>
      <v-col v-else cols="5">
        <v-row justify="end">
          <v-btn medium fab class="button" @click="adjustTime(-30)">
            <v-icon>mdi-rewind-30</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(-10)">
            <v-icon>mdi-rewind-10</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(10)">
            <v-icon>mdi-fast-forward-10</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(30)">
            <v-icon>mdi-fast-forward-30</v-icon>
          </v-btn>
        </v-row>
      </v-col>
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
      // console.log("in canMarkEnd", this.startTime, this.localTimeCursor);
      // console.log(enabled);
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
