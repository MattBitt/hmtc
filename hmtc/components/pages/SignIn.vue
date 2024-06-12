<template>
  <v-container class="main-container">
    <v-flex xs12 class="text-xs-center" mt-5>
      <h1>Sign In</h1>
    </v-flex>
    <v-flex xs12 sm6 offset-sm3 mt-3>
      <form>
        <v-layout column>
          <v-flex>
            <v-text-field
              v-model="emailValue"
              name="email"
              label="Email"
              id="email"
              type="email"
              required
            ></v-text-field>
          </v-flex>
          <v-flex>
            <v-text-field
              v-model="passwordValue"
              name="password"
              label="Password"
              id="password"
              type="password"
              required
            ></v-text-field>
          </v-flex>
          <v-flex class="text-xs-center" mt-5>
            <v-btn color="primary" @click="login_clicked()">Sign In</v-btn>
            <v-btn color="error" @click="forgot_password_clicked()"
              >Forgot Password</v-btn
            >
          </v-flex>
        </v-layout>
      </form>
    </v-flex>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    name: "SignIn",
    emailValue: "mizzle@gmail.com",
    passwordValue: "password",
  }),
};
</script>
<style>
.main-container {
  border: 4px solid green;
  min-height: 100vh;
}
</style>
