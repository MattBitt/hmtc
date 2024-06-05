<template>
  <v-card min-height="80vh">
    <div class="sidebar-header">
      <v-icon size="x-large">mdi-home</v-icon>
      <a href="/">HMTC</a>
    </div>
    <div class="sidebar-subheader">
      <p>{{ version }}</p>
    </div>

    <v-divider></v-divider>

    <v-list>
      <v-list-item v-for="(item, i) in items" :key="i" :value="item">
        <v-btn
          class="sidebar-button"
          @click="sidebar_clicked(item.text)"
          outlined
        >
          <v-icon>{{ item.icon }}</v-icon
          >{{ item.text }}
        </v-btn>
      </v-list-item>
    </v-list>
    <v-divider></v-divider>
    <v-list class="bottom-list">
      <v-list-item v-for="(item, i) in other_items" :key="i" :value="item">
        <v-btn
          class="sidebar-button"
          @click="sidebar_clicked(item.text)"
          outlined
        >
          <v-icon>{{ item.icon }}</v-icon
          >{{ item.text }}
        </v-btn>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    items: [
      { text: "Recent", icon: "mdi-history", url: "/recent" },

      { text: "Videos", icon: "mdi-video", url: "/videos" },
      {
        text: "Playlists",
        icon: "mdi-playlist-music",
        url: "/playlists",
      },
      { text: "Channels", icon: "mdi-view-list", url: "/channels" },
    ],
    other_items: [
      { text: "Settings", icon: "mdi-settings", url: "/settings" },
      { text: "About", icon: "mdi-information", url: "/about" },
      { text: "Logout", icon: "mdi-logout", url: "/logout" },
    ],
    version: "0.0.0",
  }),
};
</script>
<style>
.sidebar-header {
  font-size: 40px;
  font-weight: bolder;
  padding: 0.1em;
  text-align: center;
  margin-bottom: 0px;
  font-family: "Verdana", sans-serif;
}

.sidebar-subheader {
  font-size: 0.8em;

  padding: 0.1em;
  text-align: center;
  margin-bottom: 10px;
  font-family: "Verdana", sans-serif;
}

.sidebar-button {
  display: block;
  margin-left: 1rem;
  padding: 1rem 1.25rem;
  font-family: sans-serif;
  font-size: 1.5rem;
  text-decoration: none;
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
</style>
