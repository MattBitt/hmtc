<template>
  <div id="app">
    <template>
      <v-container fluid class="pa-0">
        <h1>{{ comp1 }}</h1>
        <v-divider></v-divider>
        <div style="background:red; padding:15px">
          Children will appear below:<br>
          <jupyter-widget v-for="child in children" :key="child" :widget="child"></jupyter-widget>
        </div>
        <v-divider></v-divider>
        <h1>{{ comp2 }}</h1>
        <v-divider></v-divider>
      </v-container>
    </template>
  </div>
</template>
<script>
export default {
  data: () => ({
    comp1: "ASDF",
    comp2: "QWER",
  }),

  methods: {
    season(val) {
      return this.icons[val];
    },
  },
};
</script>
<style></style>
