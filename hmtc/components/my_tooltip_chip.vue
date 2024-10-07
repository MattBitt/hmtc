<template>
  <div>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-chip
          :class="myclass"
          v-bind="attrs"
          v-on="on"
          @click="$emit('myclicked', { message: message })"
        >
          <v-icon class="">{{ icon }}</v-icon>
        </v-chip>
      </template>
      <span>{{ message }}</span>
    </v-tooltip>
  </div>
</template>
<script>
module.exports = {
  name: "MyToolTipChip",
  props: { icon: String, message: String, myclass: String },
  emits: ["myclicked"],
};
</script>
