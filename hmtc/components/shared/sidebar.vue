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
    <div class="text-start">
      <v-menu bottom offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn class="button" v-bind="attrs" v-on="on">
            <v-icon>mdi-video</v-icon>Videos
            <v-icon right>mdi-menu-down</v-icon>
          </v-btn>
        </template>

        <v-list>
          <v-list-item v-for="(item, index) in videoItems" :key="item.url">
            <v-btn class="button" @click="sidebar_clicked(item.url)">
              <v-icon class="px-4">{{ item.icon }}</v-icon
              >{{ item.text }}
            </v-btn>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
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
    <div>
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn class="button" v-bind="attrs" v-on="on"> old functions </v-btn>
        </template>
        <v-list>
          <v-list-item v-for="(item, index) in old_items" :key="index">
            <v-list-item-title
              ><v-btn class="button" @click="sidebar_clicked(item.url)">
                <v-icon class="px-4">{{ item.icon }}</v-icon
                >{{ item.text }}
              </v-btn></v-list-item-title
            >
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    items: [
      { text: "Albums", icon: "mdi-album", url: "/albums" },
      { text: "Tracks", icon: "mdi-music-clef-treble", url: "/tracks" },
      { text: "Now Playing", icon: "mdi-play-speed", url: "/now-playing" },
    ],
    items2: [
      { text: "Stats", icon: "mdi-graph", url: "/stats" },
      { text: "Series", icon: "mdi-shape", url: "/series" },
      { text: "Youtube Series", icon: "mdi-youtube", url: "/youtube-series" },
      { text: "Channels", icon: "mdi-view-list", url: "/channels" },
      { text: "Sections", icon: "mdi-youtube", url: "/sections" },
      { text: "Files", icon: "mdi-folder", url: "/files" },
      { text: "Topics", icon: "mdi-book-open", url: "/topics" },
    ],
    old_items: [
      { text: "Stats", icon: "mdi-chart-areaspline", url: "/library-stats" },
      { text: "Recent", icon: "mdi-history", url: "/recent" },
      { text: "Now Playing", icon: "mdi-play-speed", url: "/now-playing" },
      { text: "Jellyfin Info", icon: "mdi-information", url: "/jellyfin-info" },
    ],
    videoItems: [
      { text: "Add New Video", icon: "mdi-plus-circle", url: "/add-video" },
      { text: "Videos (Unique)", icon: "mdi-video", url: "/videos" },
      { text: "Videos (all)", icon: "mdi-video", url: "/videos/all" },
      {
        text: "Videos (No sections)",
        icon: "mdi-video",
        url: "/videos/sections/none",
      },
      {
        text: "Videos (With sections)",
        icon: "mdi-video",
        url: "/videos/sections/some",
      },
      {
        text: "WW (HAS Superchats)",
        icon: "mdi-video",
        url: "/videos/wednesdays/have",
      },
      {
        text: "WW (NO Superchats)",
        icon: "mdi-video",
        url: "/videos/wednesdays/need",
      },
    ],
    other_items: [
      { text: "Settings", icon: "mdi-settings", url: "/settings" },

      { text: "Files", icon: "mdi-folder", url: "/files-panel" },
      { text: "Sandbox", icon: "mdi-shovel", url: "/sandbox" },
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
