<template>
  <div>
    <h5-audio-controls
      ref="h5AudioControls"
      :src="src"
      :position="position"
      :buttonSize="buttonSize"
      :iconSize="iconSize"
      :playIcon="playIcon"
      :pauseIcon="pauseIcon"
      :autoPlay="autoPlay"
    />

    <!-- This is an external control button to simulate methods -->
    <v-btn @click="trigger">Trigger</v-btn>
    <v-btn @click="trigger2">Trigger2</v-btn>
  </div>
</template>

<script>
import playIcon from "./images/icon-play.png";
import pauseIcon from "./images/icon-pause.png";

export default {
  data: () => ({
    src: "https://www.xxx.com/foo.mp3",
    position: "left-top",
    buttonSize: "15vw",
    iconSize: "12vw",
    playIcon,
    pauseIcon,
    autoPlay: true,
  }),

  methods: {
    trigger() {
      if (this.$refs.h5AudioControls.isPlaying()) {
        this.$refs.h5AudioControls.pause();
      } else {
        this.$refs.h5AudioControls.play();
      }
    },
  },
};
</script>
