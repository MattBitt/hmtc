<template>
  <div>
    <v-sheet elevation="12" height="100%" width="90%">
      <v-tabs v-model="tabs" center-active>
        <v-tab v-for="item in tabItems" :key="item.id"> {{ item.id }} </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tabs">
        <v-tab-item v-for="item in tabItems" :key="item.id">
          <v-container>
            <v-row>
              {{ item.id }} - {{ item.text }} - {{ timeString(item.start) }} -
              {{ timeString(item.end) }}</v-row
            >
            <v-row></v-row>
            <v-row>
              <v-col v-for="topic in item.topics" :key="topic.id">
                <v-chip :key="topic.id">
                  {{ topic.id }} - {{ topic.text }}</v-chip
                >
              </v-col>
            </v-row>
          </v-container>
        </v-tab-item>
      </v-tabs-items>
    </v-sheet>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tabs: 0,
      tabItems: [
        {
          id: 1,
          text: "Tab 1",
          start: 0,
          end: 123456,
          topics: [{ id: 1, text: "blue" }],
        },
      ],
    };
  },
  methods: {
    timeString(ms) {
      return new Date(ms).toLocaleTimeString();
    },
  },
};
</script>
