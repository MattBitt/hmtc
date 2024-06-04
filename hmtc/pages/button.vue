<template>
  <v-card width="100%" min-height="80vh">
    <v-list>
      <v-list-item>
        <span class="ma-10">HMTC - 0.1.0</span>
      </v-list-item>
    </v-list>

    <v-divider></v-divider>

    <v-list :lines="true" density="compact" nav>
      <v-list-item v-for="(item, i) in items" :key="i" :value="item">
        <p>
          <span>
            <v-icon>{{ item.icon }}</v-icon> </span
          ><a :href="item.url" class="mx-1">{{ item.text }} </a>
        </p>
        <v-spacer></v-spacer>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    items: [
      { text: "Recent", icon: "mdi-history", url: "/recent" },

      { text: "Videos", icon: "mdi-video", url: "/media/videos" },
      {
        text: "Playlists",
        icon: "mdi-playlist-music",
        url: "/media/playlists",
      },
      { text: "Channels", icon: "mdi-view-list", url: "/media/channels" },

      { text: "Logout", icon: "mdi-logout", url: "/logout" },
      { text: "Settings", icon: "mdi-settings", url: "/settings" },
      { text: "About", icon: "mdi-information", url: "/about" },
    ],
  }),
};
</script>
