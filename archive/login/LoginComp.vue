<template>
  <v-app>
    <v-content>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="10">
            <v-card class="elevation-12">
              <!-- <v-window v-model="step"> -->
              <v-window>
                <v-window-item :value="1">
                  <v-row>
                    <v-col cols="12" md="8">
                      <v-card-text class="mt-8">
                        <h1
                          class="text-center display-2 mb-4 light-blue--text text--darken-3"
                        >
                          Sign in
                        </h1>

                        <v-form class="mt-4">
                          <v-text-field
                            label="Email"
                            name="Email"
                            prepend-icon="email"
                            type="text"
                            color="blue accent-3"
                          ></v-text-field>
                          <v-text-field
                            id="password"
                            label="Password"
                            name="Password"
                            prepend-icon="password"
                            type="password"
                            color="red accent-3"
                          ></v-text-field>
                        </v-form>
                      </v-card-text>
                      <div class="text-center">
                        <v-btn
                          :href="`media/videos`"
                          rounded
                          color="white--text light-blue"
                          >Sign in</v-btn
                        >
                      </div>
                      <div class="text-center mt-4 mb-6">
                        <v-btn
                          @click="forgot_password()"
                          rounded
                          color="error darken-1"
                          >Forgot password?</v-btn
                        >
                      </div>
                    </v-col>
                    <v-col cols="12" md="4" class="light-blue darken-2">
                      <v-card-text class="white--text mt-12">
                        <h1 class="text-center display-1">Hi, there</h1>
                        <h3 class="text-center mt-2">
                          Sign up if you still don't have an account
                        </h3>
                      </v-card-text>
                      <div class="text-center">
                        <v-btn rounded outlined dark @click="register()"
                          >Sign up</v-btn
                        >
                      </div>
                    </v-col>
                  </v-row>
                </v-window-item>
              </v-window>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
export default {
  data: () => ({
    step: 1,
  }),
  methods: {},
  mounted: () => {
    console.log("mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {},
};
</script>
