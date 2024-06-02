<template>
  <v-carousel
    height="400"
    hide-delimiter-background
    show-arrows
    v-model="pindex"
  >
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

    <v-carousel-item v-for="(slide, i) in slides" :color="colors[i]" :key="i">
      <v-sheet height="100%">
        <v-card class="text-center" dark>
          <v-chip>{{ slide.id }}</v-chip>
          <div class="mizzle">{{ slide.start_str }} - {{ slide.end_str }}</div>
          <text-subtitle-1 class="mizzle">
            {{ slide.section_type }}
          </text-subtitle-1>
          <v-cardtext class="mizzle"
            >Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Sed</v-cardtext
          >
          <v-cardtext class="mizzle" v-if="slide.selected == true"
            >asdf{{ slide.selected }}fdsa</v-cardtext
          >
          <v-divider></v-divider>
          <v-card-actions class="justify-center">
            <v-btn outlined v-on:click.stop="first_event(slide.id)">
              First Event >
            </v-btn>
            <v-btn @click="clicked(key)">Key</v-btn>
            <v-btn @click="clicked()"> Extend 5s > </v-btn>
            <v-btn @click="clicked()"> Extend 5s > </v-btn>
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
    colors: ["red", "blue", "green", "orange", "purple", "pink"],
    pindex: 0,
  }),
  methods: {
    clicked: function (event) {
      console.log("Button was clicked and the event is: ", event);
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
