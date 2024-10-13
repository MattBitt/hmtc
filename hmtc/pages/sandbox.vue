<!-- Template created on 10/12/24 as a base for child vue components -->
<template>
  <v-container>
    <v-row v-if="choosingFromExisting">
      <AutoComplete
        v-model="itemModel"
        :items="items"
        label="Album"
        itemText="title"
        itemValue="id"
        icon="mdi-album"
        :isEditing="true"
        @selectItem="selectAlbum"
        @clearItem="clearAlbum"
      >
      </AutoComplete>
      <v-btn @click="choosingFromExisting = false"
        ><v-icon>mdi-cancel</v-icon></v-btn
      >
    </v-row>
    <v-row v-else>
      <v-col cols="8">
        <CreateNewAlbumModal @createAlbum="addNewAlbum" />
      </v-col>
      <v-col cols="4">
        <v-btn @click="choosingFromExisting = true"
          ><v-icon>mdi-cancel</v-icon></v-btn
        >
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
module.exports = {
  name: "AlbumSelectorRow",
  props: { items: Array, isEditing: Boolean },
  emits: ["addNewItem", "selectItem", "clearItem"],
  data() {
    return {
      itemModel: null,
      choosingFromExisting: false,
      items: [
        { id: 1, title: "Album 1" },
        { id: 2, title: "Album 2" },
        { id: 3, title: "Album 3" },
      ],
    };
  },
  methods: {
    addNewAlbum(val) {
      console.log("addNewAlbum", val);
      this.create_album(val);
    },
    selectAlbum(val) {
      console.log("selectAlbum", val);
    },
    clearAlbum(val) {
      console.log("clearAlbum", val);
    },
  },
  created() {},
  computed: {},
};
</script>
<style></style>
