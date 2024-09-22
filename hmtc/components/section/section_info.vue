<!-- Started working on this on 9/21/24 -->
<template>
  <v-row>
    <v-col cols="6">
      <v-row justify="center" class="mb-6">
        <v-btn class="button" @click="adjustStartToCurrent()">
          Sync Start to Jellyfin
        </v-btn>
      </v-row>
      <v-row justify="center" class="mb-6">
        <span class="seven-seg">{{ this.timeString(item.start) }}</span>
      </v-row>
      <v-row justify="center">
        <v-btn xs class="button" @click="setStartTime(-5)"> -5 </v-btn>
        <v-btn xs class="button" @click="setStartTime(-1)"> -1 </v-btn>
        <v-btn xs class="button" @click="setStartTime(-0.25)"> -0.25 </v-btn>
        <v-btn xs class="button" @click="setStartTime(+0.25)"> +0.25 </v-btn>
        <v-btn xs class="button" @click="setStartTime(+1)"> +1 </v-btn>
        <v-btn xs class="button" @click="setStartTime(+5)"> +5 </v-btn>
      </v-row>
      <v-row justify="center" class="mb-6">
        <v-btn class="button" @click="loopStartJellyfin()">
          Play in Jellyfin
        </v-btn>
      </v-row>
    </v-col>
    <v-col cols="6">
      <v-row justify="center" class="mb-6">
        <v-btn class="button" @click="adjustEndToCurrent()">
          Jellyfin Time
        </v-btn>
      </v-row>
      <v-row justify="center" class="mb-6">
        <span class="seven-seg">{{ this.timeString(item.end) }}</span>
      </v-row>
      <v-row justify="center">
        <v-btn xs class="button" @click="setEndTime(-5)"> -5 </v-btn>
        <v-btn xs class="button" @click="setEndTime(-1)"> -1 </v-btn>
        <v-btn xs class="button" @click="setEndTime(-0.25)"> -0.25 </v-btn>
        <v-btn xs class="button" @click="setEndTime(+0.25)"> +0.25 </v-btn>
        <v-btn xs class="button" @click="setEndTime(+1)"> +1 </v-btn>
        <v-btn xs class="button" @click="setEndTime(+5)"> +5 </v-btn>
      </v-row>
      <v-row justify="center" class="mb-6">
        <v-btn class="button" @click="loopEndJellyfin()">
          Play in Jellyfin
        </v-btn>
      </v-row>
    </v-col>
  </v-row>
</template>

<script>
export default {
  data() {
    return {
      items: [
        {
          section_type: "INITIAL",
          start: 0,
          end: 0,
          id: 682148,
        },
      ],
    };
  },

  computed: {},

  watch: {},

  methods: {
    setStartTime(value) {
      if (this.editedItem.start + value * 1000 >= 0) {
        this.editedItem.start += value * 1000;
        this.startStringJS = this.timeString(this.editedItem.start);
      }
    },
    setEndTime(value) {
      this.editedItem.end += value * 1000;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
    timeString(value) {
      const date = new Date(null);
      date.setSeconds(value / 1000); // specify value for SECONDS here
      return date.toISOString().slice(11, 19);
    },
    loopStartJellyfin() {
      this.loop_jellyfin(this.editedItem.start);
    },
    // Jellyfin Looping delay defined below
    loopEndJellyfin() {
      this.loop_jellyfin(this.editedItem.end - 1);
    },

    adjustStartToCurrent() {
      // this doesn't work since current_postion doesn't change
      // need to call it from python
      this.editedItem.start = this.current_position;
      this.startStringJS = this.timeString(this.editedItem.start);
    },

    adjustEndToCurrent() {
      this.editedItem.end = this.current_position;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
  },
};
</script>
<style>
.seven-seg {
  font-family: "mySevenSegDisplay";
  font-size: 3em;
  color: var(--primary) !important;
  margin: 10px;
}
</style>
