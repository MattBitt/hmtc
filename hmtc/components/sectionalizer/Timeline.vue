<template>
  <v-card>
    <div
      class="timeline-container"
      :style="{ width: timelineWidth + 'px', height: '60px', position: 'relative' }"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseUp"
    >
      <!-- Base timeline -->
      <v-btn
        class="timeline-base"
        @mousedown="handleMouseDown"
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
            @mousedown.stop="handleMouseDown"
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
      hasUpdateFn: !!this.event_update_video_time,
    });
  },

  data() {
    return {
      timelineWidth: 600,
      isDragging: false,
      baseRect: null,
      localVideoTime: 0,
      sliderWidth: 4,
    };
  },

  watch: {
    videoTime(newVal) {
      console.log("videoTime changed:", newVal);
      if (!this.isDragging) {
        this.localVideoTime = newVal;
      }
    },
  },

  methods: {
    timeToPosition(time) {
      if (this.totalDuration <= 0) return 0;
      const position =
        (time / this.totalDuration) * (this.timelineWidth - this.sliderWidth);
      console.log("Converting time to position:", { time, position });
      return position;
    },

    positionToTime(pos) {
      if (this.timelineWidth <= this.sliderWidth) return 0;
      const time = (pos / (this.timelineWidth - this.sliderWidth)) * this.totalDuration;
      console.log("Converting position to time:", { pos, time });
      return time;
    },

    handleMouseDown(e) {
      console.log("Mouse down event triggered");
      this.isDragging = true;
      this.baseRect = e.target.closest(".timeline-container").getBoundingClientRect();
      this.updateTimeFromEvent(e);
    },

    handleMouseMove(e) {
      if (this.isDragging) {
        console.log("Mouse move while dragging");
        this.updateTimeFromEvent(e, true);
      }
    },

    handleMouseUp(e) {
      console.log("Mouse up event triggered, isDragging:", this.isDragging);
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

      let clickX = e.clientX - this.baseRect.left;
      clickX = Math.max(0, Math.min(clickX, this.timelineWidth - this.sliderWidth));

      const newTime = Math.max(
        0,
        Math.min(this.positionToTime(clickX), this.totalDuration)
      );
      console.log("Calculated new time:", newTime, "isDragging:", isDragging);

      this.localVideoTime = newTime;

      if (!isDragging) {
        console.log("Attempting to update video time to:", newTime);
        if (typeof this.update_video_time !== "function") {
          console.error("update_video_time is not a function:", this.update_video_time);
          return;
        }
        try {
          this.update_video_time(newTime);
          console.log("Successfully called update_video_time");
        } catch (error) {
          console.error("Error calling update_video_time:", error);
        }
      }
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
}
</style>
```
