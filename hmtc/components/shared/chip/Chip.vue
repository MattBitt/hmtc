<template>
  <div>
    <v-chip :color="color" :close="closable" @click:close="closeItem">
      <span class="chipText">{{ item }}</span>
    </v-chip>
  </div>
</template>

<script>
module.exports = {
  name: "Chip",
  props: { item: String, closable: Boolean, color: String },
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
<style>
.chipText {
  font-weight: 600;
  font-size: 1.1rem;
}
</style>
