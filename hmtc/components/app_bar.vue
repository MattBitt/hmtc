<template>
  <v-layout>
    <v-app-bar app color="blue" dark elevation="4">
      <v-app-bar-nav-icon
        variant="text"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>
      <v-toolbar-title>HMTC</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-row justify="space between">
        <v-btn icon="mdi-magnify" variant="text">Magnify</v-btn>

        <v-btn icon="mdi-filter" variant="text">Filter</v-btn>

        <v-btn icon="mdi-dots-vertical" variant="text">Hamburger</v-btn>
      </v-row>

      <!-- <v-btn
      v-for="link in links"
      :key="`${link.label}-header-link`"
      text
      rounded
      :href="link.url"
      >{{ link.label }}</v-btn
    > -->
      <!-- :location="$vuetify.display.mobile ? 'bottom' : undefined" -->
      <v-btn @click="toggleTheme" text rounded>Toggle Theme</v-btn>
    </v-app-bar>
    <v-navigation-drawer>
      <v-list-item title="My Application" subtitle="Vuetify"></v-list-item>
      <v-divider></v-divider>
      <v-list-item link title="List Item 1"></v-list-item>
      <v-list-item link title="List Item 2"></v-list-item>
      <v-list-item link title="List Item 3"></v-list-item>
    </v-navigation-drawer>
  </v-layout>
</template>

<script>
export default {
  name: "App",
  methods: {
    toggleTheme() {
      this.$vuetify.theme.themes.dark.anchor = "#41B883";
      this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
    },
  },

  data: () => ({
    drawer: false,
    group: null,
    links: [
      {
        label: "Home",
        url: "/",
      },
      {
        label: "Channels",
        url: "/media/channels",
      },
      {
        label: "Videos",
        url: "/videos",
      },
      {
        label: "Playlists",
        url: "/media/playlists",
      },
    ],
    items: [
      {
        title: "Foo",
        value: "foo",
      },
      {
        title: "Bar",
        value: "bar",
      },
      {
        title: "Fizz",
        value: "fizz",
      },
      {
        title: "Buzz",
        value: "buzz",
      },
    ],
  }),
};
</script>
