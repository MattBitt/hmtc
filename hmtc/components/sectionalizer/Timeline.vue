<template>
  <v-card @keydown="handleKeydown" tabindex="0" ref="timelineCard" class="timeline-card">
    <div
      class="timeline-container"
      :style="{ width: timelineWidth + 'px', height: '60px', position: 'relative' }"
      @mousemove="handleMove"
      @mouseup="handleEnd"
      @mouseleave="handleEnd"
      @touchmove="handleMove"
      @touchend="handleEnd"
      @touchcancel="handleEnd"
    >
      <!-- Base timeline -->
      <v-btn
        class="timeline-base"
        @mousedown="handleStart"
        @touchstart="handleStart"
        :style="{
          width: '100%',
          height: '12px',
          background: '#ddd',
          position: 'absolute',
          top: '24px',
          cursor: 'pointer',
        }"
      >
      </v-btn>

      <!-- Current time indicator -->
      <v-tooltip :text="'Current: ' + localVideoTime.toFixed(2) + 's'">
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            @mousedown.stop="handleStart"
            @touchstart.stop="handleStart"
            :style="{
              width: sliderWidth + 'px',
              height: '20px',
              background: 'red',
              position: 'absolute',
              left: timeToPosition(localVideoTime) + 'px',
              top: '20px',
              cursor: 'ew-resize',
              transform: 'translateX(-50%)',
            }"
          >
          </v-btn>
        </template>
      </v-tooltip>
    </div>
  </v-card>
</template>

<script>
module.exports = {
  props: {
    videoTime: {
      type: Number,
      required: true,
    },
    localVideoTime: {
      type: Number,
      required: true,
    },
    totalDuration: {
      type: Number,
      required: true,
    },
    event_update_video_time: {
      type: Function,
      required: true,
    },
  },

  created() {
    console.log("Component created. Props:", {
      videoTime: this.videoTime,
      totalDuration: this.totalDuration,
      hasUpdateFn: !!this.update_video_time,
    });
  },

  data() {
    return {
      timelineWidth: 600,
      isDragging: false,
      baseRect: null,
      sliderWidth: 4,
      lastUpdateTime: 0,
      updateThreshold: 100, // Minimum ms between updates to Python
    };
  },

  mounted() {
    this.$refs.timelineCard.$el.focus();
  },

  methods: {
    getEventPosition(e) {
      // Handle touch events
      if (e.touches || e.changedTouches) {
        const touch = e.touches ? e.touches[0] : e.changedTouches[0];
        return touch ? touch.clientX : null;
      }
      // Handle mouse events
      return e.clientX;
    },

    handleStart(e) {
      console.log("Start event triggered");
      e.preventDefault();
      this.isDragging = true;
      this.baseRect = e.target.closest(".timeline-container").getBoundingClientRect();
      this.updateTimeFromEvent(e);
    },

    handleMove(e) {
      if (this.isDragging) {
        console.log("Move while dragging");
        e.preventDefault();
        this.updateTimeFromEvent(e, true);
      }
    },

    handleEnd(e) {
      console.log("End event triggered, isDragging:", this.isDragging);
      if (this.isDragging) {
        // Force final update
        this.lastUpdateTime = 0;
        this.updateTimeFromEvent(e, false);
      }
      this.isDragging = false;
      this.baseRect = null;
    },

    updateTimeFromEvent(e, isDragging = false) {
      if (!this.baseRect) {
        console.log("No baseRect available");
        return;
      }

      const clientX = this.getEventPosition(e);
      if (clientX === null) {
        console.log("Invalid event position");
        return;
      }

      // Calculate click position relative to timeline
      let clickX = clientX - this.baseRect.left - this.sliderWidth / 2;

      // Enforce boundaries
      clickX = Math.max(0, Math.min(clickX, this.timelineWidth - this.sliderWidth));

      const newTime = Math.max(
        0,
        Math.min(this.positionToTime(clickX), this.totalDuration)
      );

      const currentTime = Date.now();
      const timeSinceLastUpdate = currentTime - this.lastUpdateTime;

      // Always update local display
      this.localVideoTime = newTime;

      // Only send updates to Python if:
      // 1. We're not dragging (final position)
      // 2. OR enough time has passed since last update
      // 3. OR it's the first update of a drag
      if (
        !isDragging ||
        timeSinceLastUpdate > this.updateThreshold ||
        !this.lastUpdateTime
      ) {
        console.log("Sending update to Python:", newTime);
        this.update_video_time(newTime);
        this.lastUpdateTime = currentTime;
      }
    },

    timeToPosition(time) {
      if (this.totalDuration <= 0) return 0;
      // Calculate position with slider half-width offset
      const position =
        (time / this.totalDuration) * (this.timelineWidth - this.sliderWidth);
      return position;
    },

    positionToTime(pos) {
      if (this.timelineWidth <= this.sliderWidth) return 0;
      const time = (pos / (this.timelineWidth - this.sliderWidth)) * this.totalDuration;
      return time;
    },

    handleTimelineClick(e) {
      this.updateTimeFromEvent(e);
    },

    handleKeydown(e) {
      const STEP = 10.0;

      switch (e.key) {
        case "ArrowLeft":
          e.preventDefault();
          const prevTime = Math.max(0, this.localVideoTime - STEP);
          console.log("Left arrow pressed, new time:", prevTime);
          this.update_video_time(prevTime);
          break;

        case "ArrowRight":
          e.preventDefault();
          const nextTime = Math.min(this.totalDuration, this.localVideoTime + STEP);
          console.log("Right arrow pressed, new time:", nextTime);
          this.update_video_time(nextTime);
          break;
      }
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
}
</style>
```
