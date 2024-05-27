<template>
  <v-card class="text-center" :color="color" dark>
    <v-chip> Chip </v-chip>
    <v-card-text>
      <v-sheet color="rgba(0, 0, 0, .12)">
        <v-text-field label="Label"></v-text-field>
      </v-sheet>
    </v-card-text>

    <v-card-text>
      <h1 class="solara-some-class">
        {{ caption }}
      </h1>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="justify-center">
      <v-btn block text @click="goto_report"> Go to Report </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style id="mycard">
.solara-some-class {
  font-weight: lighter;
}
</style>

<script>
export default {
  data: () => ({
    value: [],
  }),
  mounted: () => {
    console.log("mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {
    value: function (val) {
      console.log("value changed to", val);
    },
  },
};
</script>

data() { return { colors: [ "indigo", "warning", "pink darken-2", "red
lighten-1", "deep-purple accent-4", ], slides: ["First", "Second", "Third",
"Fourth", "Fifth"], }; }, };
