<template>
  <v-row justify="center">
    <v-menu offset-y>
      <template v-slot:activator="{ on }">
        <v-btn icon x-large v-on="on">
          <v-avatar :color="user.is_admin ? 'warning' : 'info'" size="48">
            <span class="white--text text-h5">{{ user.initials }}</span>
          </v-avatar>
        </v-btn>
      </template>
      <v-card style="height: 300px">
        <v-navigation-drawer permanent>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title class="text-h6"> HMTC </v-list-item-title>
              <v-list-item-subtitle> {{ version }} </v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>

          <v-divider></v-divider>

          <v-list dense nav>
            <v-list-item link @click="logout_user()">
              <v-list-item-icon>
                <v-icon>mdi-logout</v-icon>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>Logout</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-navigation-drawer>
      </v-card>
    </v-menu>
  </v-row>
</template>

<script>
module.exports = {
  name: "AvatarMenu",
  props: {
    user: Array,
    version: String,
  },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {
    console.log("Created", this.user.email);
  },
  computed: {},
};
</script>
<style></style>
