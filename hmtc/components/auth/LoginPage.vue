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
<style>
/* Google Fonts Link */

/* Login form styling */
.login_form {
  width: 100%;
  max-width: 435px;
  background: #fff;
  border-radius: 6px;
  padding: 41px 30px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.login_form h3 {
  font-size: 20px;
  text-align: center;
}

/* Google & Apple button styling */

.login_form .login_option {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
}

.login_form .login_option .option {
  width: calc(100% / 2 - 12px);
}

.login_form .login_option .option a {
  height: 56px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  background: #f8f8fb;
  border: 1px solid #dadaf2;
  border-radius: 5px;
  margin: 34px 0 24px 0;
  text-decoration: none;
  color: #171645;
  font-weight: 500;
  transition: 0.2s ease;
}

.login_form .login_option .option a:hover {
  background: #ededf5;
  border-color: #626cd6;
}

.login_form .login_option .option a img {
  max-width: 25px;
}

.login_form p {
  text-align: center;
  font-weight: 500;
}

.login_form .separator {
  position: relative;
  margin-bottom: 24px;
}

/* Login option separator styling */
.login_form .separator span {
  background: #fff;
  z-index: 1;
  padding: 0 10px;
  position: relative;
}

.login_form .separator::after {
  content: "";
  position: absolute;
  width: 100%;
  top: 50%;
  left: 0;
  height: 1px;
  background: #c2c2c2;
  display: block;
}

form .input_box label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
}

/* Input field styling */
form .input_box input {
  width: 100%;
  height: 57px;
  border: 1px solid #dadaf2;
  border-radius: 5px;
  outline: none;
  background: #f8f8fb;
  font-size: 17px;
  padding: 0px 20px;
  margin-bottom: 25px;
  transition: 0.2s ease;
}

form .input_box input:focus {
  border-color: #626cd6;
}

form .input_box .password_title {
  display: flex;
  justify-content: space-between;
  text-align: center;
}

form .input_box {
  position: relative;
}
</style>
