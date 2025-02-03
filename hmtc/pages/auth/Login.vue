<template>
  <div>
    <v-container class="pa-0">
      <v-row align="center" justify="space-between">
        <v-col cols="7">
          <div class="mb-4">
            <span class="text-h6 text--secondary">
              <img
                src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
                alt=""
                width="24"
                style="vertical-align: middle"
              />
              Sign in to your Account
            </span>
          </div>
          <h1 class="text-h5 mb-6">HMTC - Harry Mack Track Creator</h1>
          <v-form>
            <v-container class="pa-0">
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

              <v-row>
                <v-col cols="12" md="6">
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
                </v-col>
              </v-row>
            </v-container>
          </v-form>
          <div class="transition-wrapper">
            <div class="d-flex justify-space-between mt-8">
              <a href="/">
                <v-btn class="text-none letter-spacing-0" text>
                  Don't have an Account? Create One!
                </v-btn>
              </a>
              <v-btn
                class="text-none letter-spacing-0"
                style="min-width: 88px"
                color="primary"
                depressed
                @click="wip"
              >
                Sign In!
              </v-btn>
            </div>
            <!-- <transition :name="transitionName">
                <router-view @next="$emit('next', $event)" />
              </transition> -->
          </div>
        </v-col>
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
