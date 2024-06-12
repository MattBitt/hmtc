<template>
  <v-app>
    <v-content>
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="6">
            <v-card class="elevation-12">
              <v-window v-model="step">
                <v-window-item :value="1">
                  <v-row>
                    <v-col cols="12" md="12">
                      <v-card-text class="mt-8">
                        <h1
                          class="text-center display-2 mb-4 light-blue--text text--darken-3"
                        >
                          Type your email
                        </h1>
                        <v-form class="mt-4">
                          <v-text-field
                            label="Email"
                            name="Email"
                            prepend-icon="email"
                            type="text"
                            color="blue accent-3"
                          ></v-text-field>
                        </v-form>
                      </v-card-text>
                      <div class="text-center mb-6">
                        <v-btn rounded color="white--text light-blue"
                          >Send reset link</v-btn
                        >
                      </div>
                      <div class="text-center mb-6">
                        <v-btn
                          rounded
                          color="white--text light-blue"
                          @click="login()"
                          >Login page</v-btn
                        >
                      </div>
                      <div class="text-center mb-6">
                        <v-btn
                          rounded
                          color="white--text light-blue"
                          @click="register()"
                          >Register page</v-btn
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
