<template>
  <v-card class="" max-width="300" tile>
    <v-list>
      <v-subheader>{{ title }}</v-subheader>
      <v-list-item-group v-model="selectedItem" color="primary">
        <v-list-item v-for="(item, i) in items" :key="i">
          <v-list-item-content>
            <v-list-item-title v-text="item"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-card>
</template>

<script>
module.exports = {
  name: "MyList",
  props: { title: String, items: Array },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {},
  computed: {},
};
</script>
<style></style>
