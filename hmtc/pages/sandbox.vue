<template>
  <div id="app">
    <template>
      <v-container fluid class="pa-0">
        <v-row>
          <v-col class="pa-12">
            <v-range-slider
              :tick-labels="seasons"
              :value="[0, 1]"
              min="0"
              max="3"
              ticks="always"
              tick-size="4"
            >
              <template v-slot:thumb-label="props">
                <v-icon dark>
                  {{ season(props.value) }}
                </v-icon>
              </template>
            </v-range-slider>
          </v-col>
        </v-row>
        <v-row class="pa-0">
          <v-col>
            <div>Start</div>
            <div>04:23:00.1234</div></v-col
          >
          <v-col>
            <div>End</div>
            <div>08:14:74.1234</div></v-col
          >
          <v-col>
            <div>Duration</div>
            <div>04:23:00.1234</div></v-col
          >
        </v-row>
      </v-container>
    </template>
  </div>
</template>
<script>
export default {
  data: () => ({
    seasons: ["Winter", "Spring", "Summer", "Fall"],
    icons: ["mdi-snowflake", "mdi-leaf", "mdi-fire", "mdi-water"],
  }),

  methods: {
    season(val) {
      return this.icons[val];
    },
  },
};
</script>
<style>
.quote-box {
  background-color: lightgreen;
  width: 300px;
  padding: 5px 10px;
}

.quote-text {
  font-style: italic;
}
</style>
