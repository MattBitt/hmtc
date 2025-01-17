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
      { text: "Domain Item Tables", icon: "mdi-google-circles-extended", url: "/tables"}
    ],
    
    items2: [
      { text: "Stats", icon: "mdi-graph", url: "/dashboards/stats" },
      { text: "Files Dashboard", icon: "mdi-folder", url: "/dashboards/files" },
      { text: "Recent", icon: "mdi-history", url: "/utils/recent" },
      {
        text: "Now Playing",
        icon: "mdi-play-speed",
        url: "/utils/now-playing",
      },
      { text: "Settings", icon: "mdi-settings", url: "/utils/settings" },
    ],

    other_items: [
      { text: "Sandbox", icon: "mdi-shovel", url: "/sandbox/sandbox" },
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
