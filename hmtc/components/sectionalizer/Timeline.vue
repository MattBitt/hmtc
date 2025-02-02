<template>
  <v-card tabindex="0" ref="timelineCard" class="timeline-card">
    <div class="timeline-container">
      <v-slider
        v-model="localTimeCursor"
        :max="totalDuration"
        :min="0"
        step="1000"
        @input="onSliderInput"
        class="slider"
        hide-details
      >
        <template v-slot:append>
          <span>{{ durationString }}</span>
        </template>
      </v-slider>
    </div>

    <v-row>
      <v-col cols="5">
        <v-row justify="center">
          <span v-if="isEditingMode">
            <v-btn @click="isEditingMode = false" class="button mywarning">Cancel</v-btn>
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
        <span class="seven-seg">{{ videoTime / 1000 }}</span>
      </v-col>
      <v-col cols="5">
        <v-row justify="end">
          <v-btn medium fab class="button" @click="adjustTime(-5000)">
            <v-icon>mdi-rewind-5</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(-1000)">
            <v-icon>mdi-rewind</v-icon>
          </v-btn>
          <!-- <v-btn medium fab class="button" @click="adjustTime(-250)">
        <v-icon>mdi-step-backward</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(250)">
        <v-icon>mdi-step-forward</v-icon>
      </v-btn> -->
          <v-btn medium fab class="button" @click="adjustTime(1000)">
            <v-icon>mdi-fast-forward</v-icon>
          </v-btn>
          <v-btn medium fab class="button" @click="adjustTime(5000)">
            <v-icon>mdi-fast-forward-5</v-icon>
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
      this.localTimeCursor = newValue;
    },
  },

  computed: {},

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
