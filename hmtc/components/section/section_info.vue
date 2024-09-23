<!-- Started working on this on 9/21/24 -->
<template>
  <div id="section-info-container">
    <v-row id="section-times">
      <v-col id="start_time" cols="6">
        <v-row justify="center" class="mb-6">
          <span class="seven-seg">{{ this.timeString(item.start) }}</span>
        </v-row>

        <v-row justify="center">
          <v-col cols="4">
            <v-btn xs class="button" @click="setStartTime(-0.25)">
              -0.25
            </v-btn>
            <v-btn xs class="button" @click="setStartTime(-1)"> -1 </v-btn>
            <v-btn xs class="button" @click="setStartTime(-5)"> -5 </v-btn>
          </v-col>
          <v-col cols="4">
            <v-row justify="center" class="mb-6">
              <v-btn class="button" @click="loopStartJellyfin()"> Play </v-btn>
            </v-row>
            <v-row>
              <v-btn class="button" @click="adjustStartToCurrent()">
                Sync (jf)
              </v-btn>
            </v-row>
          </v-col>
          <v-col cols="4">
            <v-btn xs class="button" @click="setStartTime(+0.25)">
              +0.25
            </v-btn>
            <v-btn xs class="button" @click="setStartTime(+1)"> +1 </v-btn>
            <v-btn xs class="button" @click="setStartTime(+5)"> +5 </v-btn>
          </v-col>
        </v-row>
      </v-col>

      <v-col id="end_time" cols="6">
        <v-row justify="center" class="mb-6">
          <span class="seven-seg">{{ this.timeString(item.end) }}</span>
        </v-row>

        <v-row justify="center">
          <v-col cols="4">
            <v-btn xs class="button" @click="setEndTime(-0.25)"> -0.25 </v-btn>
            <v-btn xs class="button" @click="setEndTime(-1)"> -1 </v-btn>
            <v-btn xs class="button" @click="setEndTime(-5)"> -5 </v-btn>
          </v-col>
          <v-col cols="4">
            <v-row justify="center" class="mb-6">
              <v-btn class="button" @click="loopEndJellyfin()"> Play </v-btn>
            </v-row>
            <v-row>
              <v-btn class="button" @click="adjustEndToCurrent()">
                Sync (jf)
              </v-btn>
            </v-row>
          </v-col>
          <v-col cols="4">
            <v-btn xs class="button" @click="setEndTime(+0.25)"> +0.25 </v-btn>
            <v-btn xs class="button" @click="setEndTime(+1)"> +1 </v-btn>
            <v-btn xs class="button" @click="setEndTime(+5)"> +5 </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  data() {
    return {
      item: {
        section_type: "INITIAL",
        start: 0,
        end: 0,
        id: 682148,
      },
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
      date.setSeconds(value / 1000);
      console.log(date.toISOString().slice(11, 19));
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
