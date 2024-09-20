<template>
  <v-card class="mx-auto" max-width="400">
    <v-span class="text-h5">Select an item</v-span>
    <v-divider></v-divider>
    <v-span class="text-h6">Selected: {{ selected.id }}</v-span>
    <v-list>
      <v-list-item-group v-model="model" mandatory color="indigo">
        <v-list-item v-for="(item, i) in items" :key="i">
          <v-list-item-icon>
            <v-icon v-text="item.icon"></v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title v-text="item.id"></v-list-item-title>
            <v-list-item-subtitle v-text="item.start"></v-list-item-subtitle>
            <v-list-item-subtitle v-text="item.end"></v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      items: [
        {
          icon: "mdi-wifi",
          text: "Wifi",
        },
        {
          icon: "mdi-bluetooth",
          text: "Bluetooth",
        },
        {
          icon: "mdi-chart-donut",
          text: "Data Usage",
        },
      ],
      model: 1,
    };
  },
  computed: {
    selected() {
      return this.items[this.model];
    },
  },
};
</script>
