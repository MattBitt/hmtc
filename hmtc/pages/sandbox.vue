<template>
  <v-container class="main-container">
    <v-row class="stage">
      <v-col cols="8" class="box bounce-7">
        <v-text class="title">HMTC</v-text>

        <v-text class="subtitle">all harry mack</v-text>

        <v-text class="subtitle">all the time..</v-text></v-col
      >
    </v-row>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    name: "Landing",
  }),
};
</script>

<style>
.main-container {
  min-height: 100vh;
}

.title {
  color: white !important;
  font-family: "Impact";
  font-size: 40px;
}
.subtitle {
  color: white !important;
  font-family: "Impact";
  font-size: 20px;
}
.stage {
  display: flex;
  height: 330px;
  width: 100%;
}
.box {
  align-self: flex-end;
  justify-content: center;
  animation-duration: 2s;
  animation-iteration-count: infinite;
  background-color: #5b7a8e;
  height: 200px;
  margin: 0 auto 0 auto;
  transform-origin: bottom;
  width: 200px;
}
.bounce-7 {
  animation-name: bounce-7;
  animation-timing-function: cubic-bezier(0.28, 0.84, 0.42, 1);
}
@keyframes bounce-7 {
  0% {
    transform: scale(1, 1) translateY(0);
  }
  10% {
    transform: scale(1.1, 0.9) translateY(0);
  }
  30% {
    transform: scale(0.9, 1.1) translateY(-100px);
  }
  50% {
    transform: scale(1.05, 0.95) translateY(0);
  }
  57% {
    transform: scale(1, 1) translateY(-7px);
  }
  64% {
    transform: scale(1, 1) translateY(0);
  }
  100% {
    transform: scale(1, 1) translateY(0);
  }
}
</style>
