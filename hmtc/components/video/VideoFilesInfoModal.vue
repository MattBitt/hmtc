<template>
  <v-menu bottom origin="center center" transition="scale-transition">
    <template v-slot:activator="{ on: menu, attrs }">
      <v-tooltip bottom>
        <template v-slot:activator="{ on: tooltip }">
          <v-badge
            :content="messages"
            :value="folder_files.length != db_files.length"
            color="#00B020"
            overlap
          >
            <v-btn icon v-bind="attrs" v-on="{ ...tooltip, ...menu }">
              <v-icon large>mdi-dots-vertical</v-icon>
            </v-btn>
          </v-badge>
        </template>
        <span>Files</span>
      </v-tooltip>
    </template>
    <v-sheet>
      <v-row>
        <v-col cols="6">
          <v-list>
            <v-list-item-title
              >Folder Files ({{ folder_files.length }})</v-list-item-title
            >
            <v-list-item v-for="(item, i) in folder_files" :key="i">
              <v-list-item-title>{{ item.name }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-col>
        <v-col cols="6">
          <v-list>
            <v-list-item-title
              >DB Files ({{ db_files.length }})</v-list-item-title
            >
            <v-list-item v-for="(item, i) in db_files" :key="i">
              <v-list-item-title>{{ item.filename }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-sheet>
  </v-menu>
</template>
<script>
module.exports = {
  name: "VideoFilesInfoModal",
  props: { folder_files: Array, db_files: Array },
  emits: [],
  data() {
    return {
      fav: true,
      menu: false,
      message: false,
      messages: 0,
      hints: true,
      items: [
        { title: "Click Me" },
        { title: "Click Me" },
        { title: "Click Me" },
        { title: "Click Me 2" },
      ],
    };
  },

  methods: {},
  created() {},
  computed: {},
};
</script>
<style></style>
