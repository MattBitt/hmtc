<template>
  <div>
    <v-card>
      <v-row justify="space-between" class="icon-square px-2 mx-1 py-1">
        <v-icon size="30" color="white">{{ icon }}</v-icon>
        <h3>{{ title }}</h3>
      </v-row>
      <v-row>
        <v-col cols="9">
          <v-row justify="center">
            <h1>{{ value }}</h1>
          </v-row>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
module.exports = {
  name: "DomainCard",
  props: { title: String, icon: String, value: Int32Array },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {},
  computed: {},
};
</script>
<style>
.icon-square {
  justify-content: center;
  align-items: center;
  background-color: var(--primary);
  color: white;
}
</style>
