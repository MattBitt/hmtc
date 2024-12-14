<template>
  <v-card class="sidebar" color="primary">
    <div class="header">
      <span class="sidebarlogo">
        <a href="/">HMTC</a>
      </span>
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
    <v-list class="top-list mt-8">
      <v-list-item v-for="(item, i) in items2" :key="i" :value="item">
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
export default {
  data: () => ({
    items: [
      { text: "Albums", icon: "mdi-album", url: "/tables/albums" },
      { text: "Artists", icon: "mdi-account", url: "/tables/artists" },
      { text: "Beats", icon: "mdi-music", url: "/tables/beats" },
      { text: "Channels", icon: "mdi-view-list", url: "/tables/channels" },
      { text: "Discs", icon: "mdi-disc", url: "/tables/discs" },
      { text: "Sections", icon: "mdi-rhombus-split", url: "/tables/sections" },
      { text: "Series", icon: "mdi-shape", url: "/tables/series" },
      { text: "Superchats", icon: "mdi-account", url: "/tables/superchats" },
      {
        text: "Superchat Segments",
        icon: "mdi-account",
        url: "/tables/superchat-segments",
      },
      { text: "Topics", icon: "mdi-book-open", url: "/tables/topics" },
      { text: "Tracks", icon: "mdi-music-clef-treble", url: "/tables/tracks" },
      { text: "Users", icon: "mdi-account", url: "/tables/users" },
      { text: "Videos (Unique)", icon: "mdi-video", url: "/tables/videos" },
      {
        text: "Youtube Series",
        icon: "mdi-youtube",
        url: "/tables/youtube-series",
      },
    ],
    items2: [
      { text: "Stats", icon: "mdi-graph", url: "/dashboards/stats" },
      { text: "Recent", icon: "mdi-history", url: "/utils/recent" },
      {
        text: "Now Playing",
        icon: "mdi-play-speed",
        url: "/utils/now-playing",
      },
      { text: "Settings", icon: "mdi-settings", url: "/utils/settings" },
    ],

    other_items: [{ text: "Sandbox", icon: "mdi-shovel", url: "/sandbox" }],
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
  color: var(--on-primary) !important;
  min-width: 180px;
  min-height: 90vh;

  & .header a {
    font-family: "LogoFont";
    text-decoration: none;
    color: var(--on-primary);
    font-size: 2em;
    font-weight: 800;
    padding: 0.1em;

    margin-bottom: 0px;
  }

  & .subheader {
    font-size: 1.2em;

    padding: 0.2em;
    text-align: center;
  }
}

.bottom-list {
  background-color: var(--primary) !important;
  position: absolute;
  bottom: 0;
  width: 100%;
}

.top-list {
  background-color: var(--primary) !important;
  display: grid;
  grid-template-columns: 100px;
  grid-gap: 5px;
}
</style>
