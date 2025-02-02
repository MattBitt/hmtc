<template>
  <div>
    <v-card>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Login to HMTC</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-container>
          <v-row>
            <v-text-field v-model="currentItem.username" label="Username"></v-text-field>
          </v-row>
          <v-row>
            <v-text-field v-model="currentItem.email" label="Email"></v-text-field>
          </v-row>

          <v-row>
            <v-text-field v-model="currentItem.password" label="Password"></v-text-field>
          </v-row>
        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="button mywarning" @click="close"> Forgot Password </v-btn>
        <v-btn class="button" text @click="login" disabled="!valid"> Login </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
module.exports = {
  name: "LoginPage",
  props: {},
  emits: [],
  data() {
    return {
      loading: false,
      currentItem: {},
      valid: false,
    };
  },
  watch: {},
  methods: {
    login() {
      this.login_user(this.currentItem);
    },
  },
};
</script>
<style>
/* removes the items per page selector*/
.v-data-footer {
  display: none;
}
</style>
