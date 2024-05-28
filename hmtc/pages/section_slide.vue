<template>
  <v-carousel height="400" hide-delimiter-background show-arrows>
    <template v-slot:prev="{ props }">
      <v-btn color="success" variant="elevated" @click="props.onClick"
        >Previous slide</v-btn
      >
    </template>
    <template v-slot:next="{ props }">
      <v-btn color="info" variant="elevated" @click="props.onClick"
        >Next slide</v-btn
      >
    </template>

    <v-carousel-item v-for="(slide, i) in slides" :key="i">
      <v-sheet height="100%">
        <v-card class="text-center" dark>
          <v-chip>{{ slide.id }}</v-chip>
          <div class="mizzle">{{ slide.start_str }} - {{ slide.end_str }}</div>
          <text-subtitle-1 class="font-weight-light">
            {{ slide.section_type }}
          </text-subtitle-1>

          <v-divider></v-divider>
          <v-card-actions class="justify-center">
            <v-btn @click="clicked()"> Extend 5s > </v-btn>
          </v-card-actions>
        </v-card>
      </v-sheet>
    </v-carousel-item>
  </v-carousel>
</template>
<script>
export default {
  data: () => ({
    avalue: "bizzle",
    slides: [],
    colors: [],
    model: 0,
  }),
  methods: {
    clicked: function () {
      console.log("Button was clicked");
    },
  },
  mounted: () => {
    console.log("📕📕📕mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {
    value: function (val) {
      console.log("value changed to", val);
    },
  },
  computed: {
    columns() {
      return;
    },
  },
};
</script>
