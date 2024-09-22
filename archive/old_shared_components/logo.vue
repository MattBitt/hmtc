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
.waviy {
  display: flex;
  margin-top: 100px;

  & span {
    font-family: LogoFont;
    font-size: 60px;
    background-color: var(--dark);
    color: var(--on-dark);
    position: relative;
    display: inline-block;

    text-transform: uppercase;
    animation: flip 2s infinite;
    animation-delay: calc(0.2s * var(--i));
  }
}

.sub-logo {
  padding: 0.2em 2em 0.2em 2em;
  font-size: 40px;
  background-color: var(--primary) !important;
  color: var(--on-primary) !important;
}

@keyframes flip {
  0%,
  80% {
    transform: rotateY(360deg);
  }
}
</style>
