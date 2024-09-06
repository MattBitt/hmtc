<template>
  <v-card class="" elevation="24">
    <v-carousel :continuous="false" :show-arrows="false" delimiter-icon="mdi-square" hide-delimiter-background
      v-model="model">
      <v-carousel-item v-for="(child, i) in children" :key="i">
        <v-sheet height="100%" tile>

          <div class="mx-2 px-2">
            <jupyter-widget :widget="child"></jupyter-widget>
          </div>
        </v-sheet>
      </v-carousel-item>
    </v-carousel>
  </v-card>
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
    model: 0,

  }),

  methods: {

  },
};

</script>