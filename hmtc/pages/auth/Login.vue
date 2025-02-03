<template>
  <div>
    <v-container class="pa-0">
      <v-row align="center" justify="center">
        <v-spacer></v-spacer>
        <v-col cols="6">
          <h1 class="text-h5 logo mb-6">HMTC</h1>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field v-model="username" label="Username" required></v-text-field>
            <v-text-field v-model="password" label="Password"></v-text-field>
          </v-form>

          <div class="d-flex justify-space-between mt-8">
            <a href="/">
              <p class="text--none">Don't Have an Account?</p>

              <p class="text--primary">Create One!</p>
            </a>
            <v-btn
              class="text-none letter-spacing-0"
              style="min-width: 88px"
              color="primary"
              depressed
              @click="validate"
            >
              Login
            </v-btn>
          </div>
        </v-col>
        <v-spacer></v-spacer>
      </v-row>
    </v-container>
  </div>
</template>

<script>
module.exports = {
  name: "LoginView",
  data() {
    return {
      valid: false,
      username: "mizzle",
      password: "matthew",
    };
  },
  methods: {
    validate() {
      this.$refs.form.validate();
      if (this.valid) {
        this.login({
          username: this.username,
          password: this.password,
        });
      } else {
      }
    },

    reset() {
      this.$refs.form.reset();
    },
    resetValidation() {
      this.$refs.form.resetValidation();
    },
  },
};
</script>
<style>
.logo {
  font-family: "LogoFont";
  color: var(--primary);
  font-size: 2em;
  font-weight: 800;
  padding: 0.1em;
  margin-bottom: 0px;
}
</style>
