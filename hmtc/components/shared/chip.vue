<template>
  <v-sheet>
    <v-chip-group active-class="primary--text" column>
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
