<template>
  <v-card @keydown="handleKeydown" tabindex="0" ref="timelineCard" class="timeline-card">
    <div class="timeline-container">
      <v-range-slider
        v-model="videoRange"
        :max="totalDuration"
        :min="0"
        step="1"
        @change="update_video_time(videoRange)"
        class="slider"
        thumb-label
        :thumb-label="formattedTime"
        ticks
        hide-details
      ></v-range-slider>
    </div>

    <!-- Existing Mark Start and Mark End Buttons -->
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
export default {
  data() {
    return {
      videoRange: [0, 600], // Start and end time range
      totalDuration: 600, // Example total duration, adjust as needed
      isEditingMode: false, // State variable for editing mode
    };
  },

  computed: {
    formattedTime() {
      const totalSeconds = Math.floor(this.videoRange[0]); // Use start time for display
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;

      // Format as HH:MM:SS
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
        2,
        "0"
      )}:${String(seconds).padStart(2, "0")}`;
    },
  },

  methods: {
    markStart() {
      this.isEditingMode = true; // Enable editing mode
      console.log("Editing mode enabled. Start time marked at:", this.videoRange[0]);
    },

    markEnd() {
      this.isEditingMode = false; // Disable editing mode
      console.log("End time marked at:", this.videoRange[1]);
    },

    update_video_time(range) {
      // Function to send the updated start and end times to the backend
      console.log("Updating video range to:", range);
      // Add your logic to update the backend here
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
  position: relative; /* Ensure relative positioning for child elements */
}

.slider {
  margin: 20px 0; /* Add margin for spacing */
}

.mark-button {
  margin: 5px; /* Add margin for spacing */
}
</style>
