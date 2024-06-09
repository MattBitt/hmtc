<template>
  <v-container>
    <v-btn
      v-for="(item, i) in items"
      :key="i"
      :value="item.value"
      @click="on_click"
      :color="color"
      :outlined="outlined"
      :rounded="rounded"
    >
      <span class="hidden-sm-and-down">{{ item.value }}</span>
      <v-icon end>{{ item.icon }}</v-icon>
    </v-btn>
  </v-container>
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
