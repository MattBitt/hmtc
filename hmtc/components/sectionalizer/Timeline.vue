<template>
  <v-card>
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
          height: '10px',
          background: '#ddd',
          position: 'absolute',
          top: '25px',
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
            }"
          >
          </v-btn>
        </template>
      </v-tooltip>

      <!-- Sections -->
      <div v-for="section in sections" :key="section.start_time">
        <v-tooltip
          v-if="section.is_complete"
          :text="
            'Type: ' +
            section.section_type +
            '\n' +
            'Start: ' +
            section.start_time.toFixed(2) +
            's\n' +
            'End: ' +
            section.end_time.toFixed(2) +
            's\n' +
            'Duration: ' +
            (section.end_time - section.start_time).toFixed(2) +
            's'
          "
        >
          <template v-slot:activator="{ props }">
            <v-btn
              v-bind="props"
              :style="{
                width:
                  timeToPosition(section.end_time) -
                  timeToPosition(section.start_time) +
                  'px',
                height: '10px',
                background: '#4CAF50',
                position: 'absolute',
                left: timeToPosition(section.start_time) + 'px',
                top: '25px',
                cursor: 'pointer',
              }"
            >
            </v-btn>
          </template>
        </v-tooltip>
      </div>
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
    sections: {
      type: Array,
      required: true,
      default: () => [],
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
    };
  },

  methods: {
    getEventPosition(e) {
      // Handle touch events
      if (e.touches || e.changedTouches) {
        const touch = e.touches ? e.touches[0] : e.changedTouches[0];
        return touch ? touch.clientX : 0;
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
      let clickX = clientX - this.baseRect.left;
      clickX = Math.max(0, Math.min(clickX, this.timelineWidth - this.sliderWidth));

      const newTime = Math.max(
        0,
        Math.min(this.positionToTime(clickX), this.totalDuration)
      );
      console.log("Time calculation:", {
        clickX,
        newTime,
        isDragging,
      });

      if (!isDragging) {
        console.log("Updating with time:", newTime);
        this.update_video_time(newTime);
      }
    },

    timeToPosition(time) {
      if (this.totalDuration <= 0) return 0;
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
  },
};
</script>

<style scoped>
.timeline-container {
  user-select: none;
  touch-action: none; /* Prevent default touch actions like scrolling */
}
</style>
```
