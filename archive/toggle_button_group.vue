<template>
  <v-col class="py-2" cols="12">
    <v-btn-toggle v-model="icon" borderless>
      <v-btn v-for="(item, i) in items" :key="i" :value="item.value">
        <span class="hidden-sm-and-down">{{ item.value }}</span>
        <v-icon end>{{ item.icon }}</v-icon>
      </v-btn>
      <!-- <v-btn value="left">
        

        <v-icon end> mdi-format-align-left </v-icon>
      </v-btn>

      <v-btn value="center">
        <span class="hidden-sm-and-down">Center</span>

        <v-icon end> mdi-format-align-center </v-icon>
      </v-btn>

      <v-btn value="right">
        <span class="hidden-sm-and-down">Right</span>

        <v-icon end> mdi-format-align-right </v-icon>
      </v-btn>

      <v-btn value="justify">
        <span class="hidden-sm-and-down">Justify</span>

        <v-icon end> mdi-format-align-justify </v-icon>
      </v-btn> -->
    </v-btn-toggle>
  </v-col>
</template>
<script>
export default {
  data: () => ({
    alignment: 1,
    formatting: [],
    value:
      "Toggle button requirements.\n\nHave at least three toggle buttons in a group\nLabel buttons with text, an icon, or",

    toggle: null,
    items: [
      { value: "Left", icon: "mdi-format-align-left" },
      { value: "Center", icon: "mdi-format-align-center" },
      { value: "Right", icon: "mdi-format-align-right" },
      { value: "Justify", icon: "mdi-format-align-justify" },
    ],
    selected: null,
    on_click: null,
    color: "blue",
    outlined: true,
    rounded: true,
  }),
};
</script>
