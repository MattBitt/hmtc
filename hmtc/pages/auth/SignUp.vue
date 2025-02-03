<template>
  <div>
    <v-container class="pa-0">
      <v-row align="center" justify="center">
        <v-spacer></v-spacer>
        <v-col cols="6">
          <div class="mb-4">
            <span class="text-h6 info--text"> Create a new Account </span>
          </div>
          <h1 class="text-h5 mb-6">HMTC</h1>
          <v-form>
            <v-container class="pa-0">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    ref="input"
                    class="mb-2"
                    label="Username"
                    name="login"
                    type="text"
                    hide-details="auto"
                    outlined
                    :error-messages="error"
                    dense
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    ref="input"
                    class="mb-2"
                    label="Email"
                    name="login"
                    type="text"
                    hide-details="auto"
                    hint="Enter a valid e-mail address."
                    persistent-hint
                    outlined
                    :error-messages="error"
                    dense
                  /> </v-col
              ></v-row>

              <v-text-field
                ref="input"
                class="mb-2"
                label="Password"
                name="login"
                type="text"
                hide-details="auto"
                outlined
                :error-messages="error"
                dense
              />

              <v-text-field
                ref="input"
                class="mb-2"
                label="Confirm"
                name="login"
                type="text"
                hide-details="auto"
                outlined
                :error-messages="error"
                dense
              />

              <div class="body-2">Must be at least 8 characters</div>
            </v-container>
          </v-form>
          <div class="transition-wrapper">
            <div class="d-flex justify-space-between mt-8">
              <a href="/api/login">
                <v-btn class="text-none letter-spacing-0" text style="margin-left: -16px">
                  Already have an Account? Login Instead
                </v-btn>
              </a>
              <v-btn
                class="text-none letter-spacing-0"
                style="min-width: 88px"
                color="primary"
                depressed
                @click="wip"
              >
                Sign Up!
              </v-btn>
            </div>
            <!-- <transition :name="transitionName">
                <router-view @next="$emit('next', $event)" />
              </transition> -->
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
      transitionName: "",
      error: "",
    };
  },
  methods: {
    wip() {
      console.log("wip");
    },
  },
};
</script>
