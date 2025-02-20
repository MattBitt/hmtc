<template>
  <div>
    <v-chip color="info" :close="closable" @click:close="closeItem"> {{ item }} </v-chip>
  </div>
</template>

<script>
module.exports = {
  name: "Chip",
  props: { item: String, closable: Boolean },
  emits: [],
  data() {
    return {};
  },
  methods: {
    closeItem() {
      this.close(this.item);
    },
  },
  created() {},
  computed: {},
};
</script>
<style></style>
