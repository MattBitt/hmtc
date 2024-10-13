<!-- Template created on 10/12/24 as a base for child vue components -->
<template>
  <v-container>
    <AutoComplete
      v-model="itemModel"
      :items="items"
      label="Album"
      itemText="title"
      itemValue="id"
      icon="mdi-album"
      :isEditing="true"
      @addNewItem="addNewAlbum"
      @selectItem="selectAlbum"
      @clearItem="clearAlbum"
    >
    </AutoComplete>
  </v-container>
</template>
<script>
module.exports = {
  name: "EmptyAutocomplete",
  props: { items: Array, isEditing: Boolean },
  emits: ["addNewItem", "selectItem", "clearItem"],
  data() {
    return {
      itemModel: null,
      isEditing: false,
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
