<template>
  <v-card tabindex="0">
    <div>
      SectionEditor<strong>{{ section.start_time }}</strong>
    </div>
  </v-card>
</template>

<script>
module.exports = {
  name: "SectionEditor",
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {
    console.log("Created!!!", this.section);
  },
  computed: {},
};
</script>

<style></style>
