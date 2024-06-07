<template>
  <v-card class="sidebar">
    <div class="header">
      <a href="/"><v-icon color="white" size="x-large">mdi-home</v-icon>HMTC</a>
    </div>
    <div class="subheader">
      <p>{{ version }}</p>
    </div>

    <v-divider></v-divider>

    <v-list class="top-list">
      <v-list-item v-for="(item, i) in items" :key="i" :value="item">
        <v-btn class="button" @click="sidebar_clicked(item.url)">
          <v-icon class="px-4">{{ item.icon }}</v-icon
          >{{ item.text }}
        </v-btn>
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list class="bottom-list">
      <v-list-item v-for="(item, i) in other_items" :key="i" :value="item">
        <v-btn class="button" @click="sidebar_clicked(item.url)">
          <v-icon class="px-4">{{ item.icon }}</v-icon
          >{{ item.text }}
        </v-btn>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
const backColor = "#5b7a8e";
export default {
  data: () => ({
    items: [
      { text: "Stats", icon: "mdi-chart-areaspline", url: "/library-stats" },
      { text: "Recent", icon: "mdi-history", url: "/recent" },
      { text: "Series", icon: "mdi-television", url: "/series" },
      { text: "Videos", icon: "mdi-video", url: "/videos" },
      {
        text: "Playlists",
        icon: "mdi-playlist-music",
        url: "/playlists",
      },

      { text: "Channels", icon: "mdi-view-list", url: "/channels" },
      { text: "Sandbox", icon: "mdi-shovel", url: "/sandbox" },
    ],
    other_items: [
      { text: "Settings", icon: "mdi-settings", url: "/settings" },
      { text: "About", icon: "mdi-information", url: "/about" },
      { text: "Logout", icon: "mdi-logout", url: "/logout" },
    ],
    version: "-0.0.0",
  }),
};
</script>
<style scoped>
.sidebar {
  font-family: "Verdana", sans-serif;
  font-weight: 600;
  font-size: 20px;
  text-align: center;
  background-color: var(--primary) !important;
  min-width: 400px;
  min-height: 90vh;

  & .header a {
    font-size: 2em;
    font-weight: 800;
    padding: 0.1em;

    margin-bottom: 0px;
    color: var(--whiteish) !important;
  }

  & .subheader {
    font-size: 1.2em;
    color: var(--whiteish);
    padding: 0.2em;
    text-align: center;
  }

  & .button {
    padding: 1rem 1.25rem;
    min-width: 300px !important;
    font-family: sans-serif;
    font-size: 1.25rem;
    font-family: "Verdana", sans-serif;
    text-decoration: none;
    font-weight: 800;
    color: var(--whiteish);
    background-color: var(--primary) !important;
  }
}
.main-container {
  border: 4px solid orange;
  min-height: 100vh;
}
.bottom-list {
  position: absolute;
  bottom: 0;
  width: 100%;
}

.top-list {
  display: grid;
  grid-template-columns: 100px;
  grid-gap: 5px;
}
</style>
