<template>
  <div>
    <v-row justify="center" class="mb-6">
      <span class="seven-seg myprimary">{{ timeString }}</span>
      <v-row justify="end">
        <v-col cols="3">
          <v-btn fab :class="[isEditing ? 'mywarning' : 'button']" @click="toggleEditMode"
            ><span v-if="isEditing"><v-icon>mdi-cancel</v-icon></span>
            <span v-else><v-icon>mdi-pencil</v-icon></span></v-btn
          >
        </v-col>
        <v-col v-if="isDirty" cols="3">
          <v-btn fab class="button" @click="updateTime">
            <v-icon> mdi-content-save </v-icon>
          </v-btn>
        </v-col>
        <v-col cols="3">
          <v-btn fab class="button" @click="loopJellyfinAt">
            <v-icon> mdi-play </v-icon>
          </v-btn>
        </v-col>
        <v-col cols="3">
          <v-btn
            fab
            class="button"
            @click="updateSectionTimeFromJellyfin(item.id, 'start')"
          >
            <v-icon>mdi-sync</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-row>
    <v-row v-if="isEditing" justify="center" class="mt-4">
      <v-btn medium fab class="button" @click="adjustTime(-60_000)">
        <v-icon>mdi-menu-left</v-icon><span>60</span>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(-30_000)">
        <v-icon>mdi-rewind-30</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(-5000)">
        <v-icon>mdi-rewind-5</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(-1000)">
        <v-icon>mdi-rewind</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(-250)">
        <v-icon>mdi-step-backward</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(250)">
        <v-icon>mdi-step-forward</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(1000)">
        <v-icon>mdi-fast-forward</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(5000)">
        <v-icon>mdi-fast-forward-5</v-icon>
      </v-btn>

      <v-btn medium fab class="button" @click="adjustTime(30_000)">
        <v-icon>mdi-fast-forward-30</v-icon>
      </v-btn>
      <v-btn medium fab class="button" @click="adjustTime(60_000)">
        <v-icon>mdi-menu-right</v-icon><span>60</span>
      </v-btn>
    </v-row>
  </div>
</template>
<script>
module.exports = {
  name: "SectionTimePanel",
  props: { initialTime: Number, sectionID: Number, video_duration: Number },

  emits: ["updateTime", "loopJellyfin", "updateSectionTimeFromJellyfin"],
  methods: {
    updateTime() {
      this.$emit("updateTime", this.sectionID, this.time);
      this.isEditing = false;
      this.isDirty = false;
    },

    toggleEditMode() {
      if (this.isEditing) {
        if (this.isDirty) {
          this.time = this.initialTime;
          this.isDirty = false;
        }
      }
      this.isEditing = !this.isEditing;
    },

    loopJellyfinAt() {
      this.$emit("loopJellyfin", this.time);
    },

    adjustTime(value) {
      const tmp_time = this.time + value;
      const durationMS = this.video_duration * 1000;
      if (tmp_time < 0) {
        this.time = durationMS; // Loop to end
      } else if (tmp_time > durationMS) {
        this.time = 0;
      } else {
        this.time = tmp_time;
      }
      this.isDirty = true;
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
      //return new Date(this.time).toISOString().slice(11, 19);
      return "some string";
    },
  },

  data() {
    return {
      time: this.initialTime,
      isEditing: false,
      isDirty: false,
    };
  },
};
</script>
