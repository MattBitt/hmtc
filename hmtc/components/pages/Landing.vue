<template>
  <v-container class="main-container">
    <v-flex xs12 class="text-xs-center" mt-10>
      <h1>HMTC</h1>
    </v-flex>
    <v-flex xs12 sm6 offset-sm3 mt-3>
      <blockquote class="blockquote text-xs-center">
        all harry mack <br />
        all the time...
      </blockquote>
    </v-flex>
    <v-flex xs12 sm6 offset-sm3 class="text-xs-center" mt-5>
      <v-btn class="child" color="primary" @click="register_clicked"
        >Sign Up</v-btn
      >
      <v-btn class="child" @click="login_clicked">Sign In</v-btn>
    </v-flex>
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
  border: 4px solid purple;
  min-height: 100vh;
}

.blockquote {
  font-family: "Impact";

  animation-duration: 3s;
  animation-name: slidein;
}

@keyframes slidein {
  from {
    margin-left: 100%;
    width: 300%;
  }

  to {
    margin-left: 0%;
    width: 100%;
  }
}
</style>
