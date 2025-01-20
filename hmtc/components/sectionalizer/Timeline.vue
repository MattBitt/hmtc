<template>
  <v-card tabindex="0" ref="timelineCard" class="timeline-card">
    <div class="timeline-container">
      <v-slider
        v-model="localVideoTime"
        :max="totalDuration"
        :min="0"
        step="1"
        @change="update_video_time(localVideoTime)"
        class="slider"
        thumb-size="36"
        :thumb-label="true"
        ticks
        hide-details
      >
        <template v-slot:thumb-label="{ value }">
          {{ formattedTime }}
        </template></v-slider
      >
    </div>

    <!-- Existing Mark Start and Mark End Buttons -->
    <div>
      <v-btn @click="markStart" :disabled="isEditingMode" class="button"
        >Mark Start</v-btn
      >
      <v-btn @click="markEnd" :disabled="!isEditingMode" class="button">Mark End</v-btn>
    </div>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      localVideoTime: 0,
      totalDuration: 600, // Example total duration, adjust as needed
      isEditingMode: false, // State variable for editing mode
    };
  },

  computed: {
    formattedTime() {
      const totalSeconds = Math.floor(this.localVideoTime);
      const hours = Math.floor(totalSeconds / 3600);
      const minutes = Math.floor((totalSeconds % 3600) / 60);
      const seconds = totalSeconds % 60;
      const timeString = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
        2,
        "0"
      )}:${String(seconds).padStart(2, "0")}`;
      console.log(hours, minutes, seconds);
      console.log(timeString);

      return timeString;
    },
  },

  methods: {
    markStart() {
      this.isEditingMode = true; // Enable editing mode
      console.log("Editing mode enabled. Start time marked at:", this.localVideoTime);
    },

    markEnd() {
      this.isEditingMode = false; // Disable editing mode
      console.log("End time marked at:", this.localVideoTime);
    },

    update_video_time(newTime) {
      // Function to send the updated time to the backend
      console.log("Updating video time to:", newTime);
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
