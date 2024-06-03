<template>
  <v-app>
    <v-content>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="10">
            <v-card class="elevation-12">
              <v-window v-model="step">
                <v-window-item :value="2">
                  <v-row class="fill-height">
                    <v-col cols="12" md="8">
                      <v-card-text class="mt-4">
                        <h1
                          class="text-center display-2 light-blue--text text--darken-3"
                        >
                          Create an account
                        </h1>
                        <div class="text-center mt-4">
                          <v-btn class="mx-2" fab color="black" outlined>
                            <v-btn
                              class="mx-2"
                              fab
                              color="blue darken-2"
                              outlined
                            >
                              <v-icon>fab fa-facebook</v-icon>
                            </v-btn>
                            <v-btn
                              class="mx-2"
                              fab
                              color="red darken-2"
                              outlined
                            >
                              <v-icon>fab fa-google</v-icon>
                            </v-btn>
                            <v-btn
                              class="mx-2"
                              fab
                              color="blue darken-3"
                              outlined
                            >
                              <v-icon>fab fa-linkedin</v-icon>
                            </v-btn>
                            <v-btn
                              class="mx-2"
                              fab
                              color="blue lighten-1"
                              outlined
                            >
                              <v-icon>fab fa-twitter</v-icon>
                            </v-btn>
                            <v-btn class="mx-2" fab color="black" outlined>
                              <v-icon>fab fa-github</v-icon>
                            </v-btn>
                            <v-btn
                              class="mx-2"
                              fab
                              color="orange darken-4"
                              outlined
                            >
                              <v-icon>fab fa-gitlab</v-icon>
                            </v-btn>
                            <v-btn
                              class="mx-2"
                              fab
                              color="blue darken-3"
                              outlined
                            >
                              <v-icon>fab fa-bitbucket</v-icon>
                            </v-btn>
                          </v-btn>
                        </div>
                        <v-form class="mt-4">
                          <v-text-field
                            label="First Name"
                            name="First Name"
                            prepend-icon="person"
                            type="text"
                            color="green accent-3"
                          ></v-text-field>
                          <v-text-field
                            label="Last Name"
                            name="Last Name"
                            prepend-icon="person"
                            type="text"
                            color="green accent-3"
                          ></v-text-field>
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
                      <div class="text-center mb-6">
                        <v-btn rounded color="white--text light-blue"
                          >Sign up</v-btn
                        >
                      </div>
                    </v-col>
                    <v-col cols="12" md="4" class="light-blue darken-2">
                      <v-card-text class="white--text mt-6">
                        <h1 class="text-center display-1">Welcome back</h1>
                      </v-card-text>
                      <div class="text-center mb-6">
                        <v-btn rounded outlined dark @click="login()"
                          >Sign in</v-btn
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
