<!-- Template created on 10/12/24 as a base for child vue components -->
<template>
  <div>
    <v-row v-if="choosingFromExisting" class="mt-0">
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
        ><v-icon>mdi-cancel</v-icon>Add New Album</v-btn
      >
    </v-row>
    <v-row v-else>
      <v-col cols="8">
        <v-dialog v-model="dialog" max-width="400px">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="button" v-bind="attrs" v-on="on"
              >Create a new Album</v-btn
            >
          </template>
          <v-card>
            <v-row class="ma-4" justify="center">
              <v-col cols="10">
                <v-text-field
                  label="Album Title"
                  v-model="albumTitle"
                ></v-text-field>

                <v-text-field
                  label="Release Date"
                  v-model="releaseDate"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn class="button" @click="close"> Cancel </v-btn>
              <v-btn class="button" text @click="saveItemToDB"> Save </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
      <v-col cols="4">
        <v-btn @click="choosingFromExisting = true"
          ><v-icon>mdi-cancel</v-icon></v-btn
        >
      </v-col>
    </v-row>
  </div>
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
      dialog: false,
      releaseDate: "",
      albumTitle: "",
    };
  },
  methods: {
    addNewAlbum(val) {
      console.log("addNewAlbum", val);
      this.create_item(val);
    },
    selectAlbum(val) {
      console.log("selectAlbum", val);
    },
    clearAlbum(val) {
      console.log("clearAlbum", val);
    },
    close() {
      this.dialog = false;
    },
    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      const args = {
        title: this.albumTitle,
        release_date: this.releaseDate,
      };
      this.$emit("createAlbum", args);
      this.close();
    },
  },
  created() {},
  computed: {},
};
</script>
<style></style>
