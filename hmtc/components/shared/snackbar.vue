<template>
  <v-snackbar
    transition="true"
    :timeout="6000"
    v-model="show2"
    :color="color"
    absolute
    top
    outlined
    right
  >
    <strong>
      <v-icon>{{ icon }}</v-icon>
      {{ message }}
    </strong>
  </v-snackbar>
</template>

<script>
export default {
  props: {
    show: Boolean,
    color: String,
    icon: String,
    message: String,
  },
  computed: {
    show2: {
      get() {
        return this.show;
      },
      set(value) {
        this.$emit("update", value);
      },
    },
  },
};
</script>
