<template>
  <div>
    <h1>Lyrics appear below</h1>
    {{ closestLyric.text }}
  </div>
</template>

<script>
export default {
  name: "LyricDisplay",
  props: {
    lyrics: {
      type: Array,
      required: true,
      validator: (value) =>
        value.every((item) => "timestamp" in item && "text" in item),
    },
    currentTimestamp: {
      type: Number,
      required: true,
    },
  },
  computed: {
    closestLyric() {
      return this.lyrics.reduce((prev, curr) => {
        return Math.abs(curr.timestamp - this.currentTimestamp) <
          Math.abs(prev.timestamp - this.currentTimestamp)
          ? curr
          : prev;
      });
    },
  },
  mounted() {
    this.intervalID = setInterval(this.update, 1000);
  },
};
</script>

<style scoped>
div {
  font-size: 1.2em;
  padding: 10px;
}
</style>
