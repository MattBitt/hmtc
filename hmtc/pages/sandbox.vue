<template>
  <div>
    <div class="faded">{{ previousLyric.text }}</div>
    <div>{{ closestLyric.text }}</div>
    <div class="faded">{{ nextLyric.text }}</div>
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
    previousLyric() {
      const index = this.lyrics.indexOf(this.closestLyric);
      return index > 0 ? this.lyrics[index - 1] : { text: "" };
    },
    nextLyric() {
      const index = this.lyrics.indexOf(this.closestLyric);
      return index < this.lyrics.length - 1
        ? this.lyrics[index + 1]
        : { text: "" };
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
.faded {
  color: rgba(128, 128, 128, 0.8);
}
</style>
