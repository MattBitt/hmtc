<template>
  <div>
    <transition-group name="fade" mode="out-in" tag="div" class="lyrics">
      <p
        v-for="(lyric, index) in displayedLyrics"
        :key="lyric.timestamp"
        :class="{ faded: index !== 1 }"
      >
        <span v-if="index === 1" class="primary--text">{{ lyric.text }}</span>
        <span v-else>{{ lyric.text }}</span>
      </p>
    </transition-group>
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
    displayedLyrics() {
      const index = this.lyrics.indexOf(this.closestLyric);
      return [
        index > 0 ? this.lyrics[index - 1] : { text: "", timestamp: -1 },
        this.closestLyric,
        ...this.lyrics.slice(index + 1, index + 2),
      ];
    },
  },
  mounted() {
    this.intervalID = setInterval(this.update, 1000);
  },
};
</script>

<style>
.lyrics {
  font-size: 2em;
  text-align: center;
  font-weight: 700;
}
.faded {
  color: rgba(128, 128, 128, 0.8);
  font-weight: 300;
}
.fade-enter-active,
.fade-leave-active {
  transition: all 1s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.fade-leave-active {
  position: absolute;
}
</style>
