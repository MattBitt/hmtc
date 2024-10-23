<template>
  <v-snackbar
    transition="true"
    v-model="show2"
    :color="color"
    absolute
    top
    outlined
    right
  >
    <strong>
      {{ message }}
    </strong>
    <v-btn color="red" text @click="show2 = !show2">Close</v-btn>
  </v-snackbar>
</template>

<script>
module.exports = {
  name: "Snackbar",
  props: {
    show: Boolean,
    color: String,
    message: String,
  },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {
    console.log(this.show);
    console.log(this.color);
    console.log(this.message);
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
<style></style>
