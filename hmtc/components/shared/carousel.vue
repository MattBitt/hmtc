<template>
  <v-container fluid>
    <v-carousel
      :continuous="false"
      :show-arrows="false"
      hide-delimiters
      hide-delimiter-background
      light
      v-model="model"
    >
      <v-carousel-item v-for="(child, i) in children" :key="i">
        <v-sheet class="mt-4" height="100%">
          <jupyter-widget :widget="child"></jupyter-widget>
        </v-sheet>
      </v-carousel-item>
    </v-carousel>
  </v-container>
</template>
<script>
export default {
  data: () => ({
    model: 0,
  }),

  methods: {},
};
</script>
