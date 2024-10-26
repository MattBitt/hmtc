<!-- Source Codes By CodingNepal - www.codingnepalweb.com -->

<template>
  <v-sheet>
    <v-container fluid class="fill-height">
      <v-row justify="center">
        <div class="login_form">
          <!-- Login form container -->
          <form action="#">
            <h3>Log in</h3>

            <!-- Email input box -->
            <div class="input_box">
              <label for="email">Email</label>
              <input
                type="email"
                id="email"
                placeholder="Enter email address"
                required
              />
            </div>

            <!-- Paswwrod input box -->
            <div class="input_box">
              <div class="password_title">
                <label for="password">Password</label>
                <a href="#">Forgot Password?</a>
              </div>

              <input
                type="password"
                id="password"
                placeholder="Enter your password"
                required
              />
            </div>

            <!-- Login button -->
            <button class="button" type="submit">Log In</button>

            <p class="sign_up">
              Don't have an account? <a href="#">Sign up</a>
            </p>
          </form>
        </div>
      </v-row>
    </v-container>
  </v-sheet>
</template>
<style></style>
