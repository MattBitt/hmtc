<template>
  <div class="text-center">
    <v-chip class="ma-2 info-chip" @click="close">
      <v-icon class="info-chip">mdi-view-list</v-icon>
      <span class="ml-2">{{ channel }}</span>
    </v-chip>
  </div>
</template>

<script>
export default {
  methods: {
    close() {
      alert("Chip close clicked");
    },
  },
};
</script>
