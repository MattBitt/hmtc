<template>
  <div class="text-center">
    <v-chip class="my-2 info-chip" @click="close">
      <v-icon class="info-chip">{{ iconName }}</v-icon>

      <span class="ml-2">{{ message }}</span>
    </v-chip>
  </div>
</template>

<script>
module.exports = {
  name: "ChildComponent",
  props: {
    iconName: {
      type: String,
      required: true,
    },
    message: {
      type: String,
      required: false,
    },
  },
  methods: {
    close() {
      alert("Chip close clicked");
    },
  },
};
</script>
