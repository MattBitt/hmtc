<template>
  <div>
    <v-row justify="center" class="mb-6">
      <span class="seven-seg myprimary">{{ timeString }}</span>
      <v-row justify="end">
        <v-btn
          :class="[isEditing ? 'mywarning' : 'myprimary']"
          @click="toggleEditMode"
          ><span v-if="isEditing"><v-icon>mdi-cancel<v-icon></span
          ><span v-else><v-icon>mdi-pencil</v-icon></span></v-btn
        >
      </v-row>
      <!-- <v-btn
        x-large
        fab
        class="button"
        @click="updateSectionTimeFromJellyfin(item.id, 'start')"
      >
        <v-icon>mdi-sync</v-icon>
      </v-btn> -->
    </v-row>
    <v-row v-if="isEditing" justify="center" class="mt-4">
      <v-btn medium fab class="" @click="adjustTime(-5000)">
        <v-icon>mdi-rewind-5</v-icon>
      </v-btn>
      <v-btn medium fab class="" @click="adjustTime(-1000)">
        <v-icon>mdi-rewind</v-icon>
      </v-btn>
      <v-btn medium fab class="" @click="adjustTime(-250)">
        <v-icon>mdi-step-backward</v-icon>
      </v-btn>
      <v-btn medium fab class="" @click="adjustTime(250)">
        <v-icon>mdi-step-forward</v-icon>
      </v-btn>
      <v-btn medium fab class="" @click="adjustTime(1000)">
        <v-icon>mdi-fast-forward</v-icon>
      </v-btn>
      <v-btn medium fab class="" @click="adjustTime(5000)">
        <v-icon>mdi-fast-forward-5</v-icon>
      </v-btn>
    </v-row>
    <v-row justify="center">
      <v-btn x-large fab class="button" @click="loopJellyfinAt(this.time)">
        <v-icon> mdi-play </v-icon>
      </v-btn>
    </v-row>
  </div>
</template>
<script>
module.exports = {
  name: "SectionTimePanel",
  props: { initialTime: Number, isEditing: Boolean },
  data() {
    return {
      time: this.initialTime,
    };
  },
  emits: ["updateTime", "loopJellyfin", "updateSectionTimeFromJellyfin"],
  methods: {
    toggleEditMode() {
      if (this.timeFormDirty && this.isEditing) {
        alert("You have unsaved changes");
        //this.timeFormDirty = false;
        return;
      }
      this.isEditing = !this.isEditing;
    },

    loopJellyfinAt(value) {
      this.$emit("loopJellyfin", value);
    },
    adjustTime(value) {
      this.time += value;
    },

    removeTopic(item_id, topic) {
      console.log("Removing topic", item_id, topic);
      const topicIndex = this.topics.findIndex((t) => t.text === topic);
      if (topicIndex !== -1) {
        this.topics.splice(topicIndex, 1);
      }

      const args = {
        item_id: item_id,
        topic: topic,
      };
      // python function
      this.$emit("removeTopic", args);
    },

    updateTimes(item_id, start, end) {
      console.log("Updating times", item_id, start, end);

      const args = {
        item_id: item_id,
        start: start,
        end: end,
      };

      this.editingTime = false;
      this.timeFormDirty = false;
      this.$emit("updateTimes", args);
    },
    updateSectionTimeFromJellyfin(item_id, time) {
      console.log("Updating time from Jellyfin", item_id, time);
      const args = {
        item_id: item_id,
        time: time,
      };
      this.$emit("updateSectionTimeFromJellyfin", args);
    },
  },
  computed: {
    timeString() {
      return new Date(this.time).toISOString().slice(11, 19);
    },
  },
};
</script>
