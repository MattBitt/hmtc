<template>
  <div>
    <v-container class="pa-0">
      <v-row align="center" justify="center">
        <v-spacer></v-spacer>
        <v-col cols="6">
          <h1 class="text-h5 logo mb-6">HMTC</h1>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field
              v-model="username"
              :rules="nameRules"
              label="Username"
              required
            ></v-text-field>
            <v-text-field
              v-model="email"
              :rules="emailRules"
              label="E-mail"
            ></v-text-field>
            <v-text-field
              v-model="password"
              :rules="passwordRules"
              label="Password"
            ></v-text-field>
            <v-text-field
              v-model="confirmPassword"
              :error-messages="passwordMatchError()"
              label="Confirm Password"
            ></v-text-field>
          </v-form>

          <div class="d-flex justify-space-between mt-8">
            <a href="/api/login">
              <p class="text--none">Already have an Account?</p>

              <p class="text--primary">Login Instead</p>
            </a>
            <v-btn
              class="text-none letter-spacing-0"
              style="min-width: 88px"
              color="primary"
              depressed
              @click="validate"
            >
              Sign Up!
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
      nameRules: [
        (v) => !!v || "Name is required",
        (v) => (v && v.length <= 10) || "Name must be less than 10 characters",
      ],
      email: "asdf@asdf.com",
      emailRules: [(v) => /.+@.+\..+/.test(v) || "E-mail must be valid"],
      password: "matthew",
      confirmPassword: "matthew",
      passwordRules: [
        (v) => !!v || "Password is required",
        (v) => (v && v.length >= 6) || "Password must be at least 6 characters",
      ],
    };
  },
  methods: {
    passwordMatchError() {
      return this.password === this.confirmPassword ? "" : "Passwords must match";
    },
    validate() {
      console.log("validating", this.valid);
      this.$refs.form.validate();
      if (this.valid) {
        this.signup({
          username: this.username,
          email: this.email,
          password: this.password,
        });
      } else {
        console.log("Form is not valid");
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
