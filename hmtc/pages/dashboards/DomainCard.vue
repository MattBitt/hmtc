<template>
  <div>
    <v-card>
      <v-row>
        <v-col class="icon-square">
          <v-icon xlarge color="white">{{ icon }}</v-icon>
        </v-col>
        <v-col cols="9">
          <h3>{{ title }}</h3>

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
  name: "EmptyComponent",
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
  border-radius: 10px;
}
</style>
