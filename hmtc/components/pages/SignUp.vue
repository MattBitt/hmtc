<template>
  <v-container class="main-container">
    <v-flex xs12 class="text-xs-center" mt-5>
      <h1>Sign Up</h1>
    </v-flex>
    <v-flex xs12 sm6 offset-sm3 mt-3>
      <form>
        <v-layout column>
          <v-flex>
            <v-text-field
              name="email"
              label="Email"
              id="email"
              type="email"
              required
            ></v-text-field>
          </v-flex>
          <v-flex>
            <v-text-field
              name="password"
              label="Password"
              id="password"
              type="password"
              required
            ></v-text-field>
          </v-flex>
          <v-flex>
            <v-text-field
              name="confirmPassword"
              label="Confirm Password"
              id="confirmPassword"
              type="password"
              required
            ></v-text-field>
          </v-flex>
          <v-flex class="text-xs-center" mt-5>
            <v-btn class="CTA" type="submit">Sign Up</v-btn>
            <a href="/"><v-btn class="Regular">Home</v-btn></a>
          </v-flex>
        </v-layout>
      </form>
    </v-flex>
  </v-container>
</template>

<script>
export default {};
</script>
<style>
.CTA {
  background-color: var(--complimentary) !important;
  color: var(--whiteish) !important;
  font-weight: 600;
}
.Regular {
  background-color: var(--primary) !important;
  color: var(--whiteish) !important;
  font-weight: 500;
}
</style>
