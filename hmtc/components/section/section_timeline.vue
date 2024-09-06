<template>
  <div id="app">
    <v-sheet class="mt-10">
      <template>
        <v-container fluid class="pa-4">
          <v-row>
            <h1>{{ timestamps.whole_start }}</h1>
            <v-col class="pa-1">
              <v-range-slider :value="[timestamps.part_start, timestamps.part_end]" :min="timestamps.whole_start"
                :max="timestamps.whole_end" tick-size="4" thumb-label="always" readonly>
              </v-range-slider>
            </v-col>
            <h1>{{ timestamps.whole_end }}</h1>
          </v-row>
        </v-container>
      </template>
    </v-sheet>
  </div>
</template>


<script>
export default {
  data: () => ({
    timestamps: {
      whole_start: 0,
      whole_end: 300,
      part_start: 60,
      part_end: 240,
    },

  }),

  methods: {

  },
};
</script>
<style></style>
