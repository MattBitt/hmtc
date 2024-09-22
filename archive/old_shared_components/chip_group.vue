<template>
  <v-sheet>
    <div class="pa-4">
      <v-chip-group active-class="primary--text" column>
        <v-chip v-for="tag in tags" :key="tag">
          {{ tag }}
        </v-chip>
      </v-chip-group>
    </div>
  </v-sheet>
</template>
<script>
export default {
  data: () => ({
    tags: [
      "Work",
      "Home Improvement",
      "Vacation",
      "Food",
      "Drawers",
      "Shopping",
      "Art",
      "Tech",
      "Creative Writing",
    ],
  }),
};
</script>
