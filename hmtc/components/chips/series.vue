<template>
  <div class="text-center">
    <v-chip class="ma-2 info-chip" @click="close">
      <v-icon class="info-chip">mdi-shape</v-icon>

      <span class="ml-2">{{ series }}</span>
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
