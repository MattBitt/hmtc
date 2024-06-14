<template>
  <v-sheet>
    <v-chip-group active-class="active" column>
      <v-chip :color="color">
        <v-icon>{{ icon }}</v-icon>
        <span class="ml-4">{{ label }}</span>
      </v-chip>
    </v-chip-group>
  </v-sheet>
</template>
<script>
export default {
  data: () => ({
    label: "Work",
    color: "pink",
    icon: "mdi-close",
  }),
  methods: {
    deleteChip() {
      console.log("Chip deleted");
    },
  },
};
</script>
<style>
.active {
  background-color: #f0f0f0;
  color: #000;
  font-size: 80px;
}
</style>
