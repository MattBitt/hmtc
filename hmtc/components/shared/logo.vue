<template>
  <v-sheet>
    <div class="waviy">
      <span style="--i: 1">H</span>
      <span style="--i: 2">M</span>
      <span style="--i: 3">T</span>
      <span style="--i: 4">C</span>
    </div>
  </v-sheet>
</template>

<script></script>

<style>
.main-container {
  min-height: 100vh;
}

.waviy span {
  font-weight: 800;
  position: relative;
  display: inline-block;
  font-size: 60px;
  color: #000;
  text-transform: uppercase;
  animation: flip 2s infinite;
  animation-delay: calc(0.2s * var(--i));
}
@keyframes flip {
  0%,
  80% {
    transform: rotateY(360deg);
  }
}
</style>
