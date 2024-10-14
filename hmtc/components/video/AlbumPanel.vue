<!-- Template created on 10/12/24 as a base for child vue components -->
<template>
  <v-dialog v-model="dialog" transition="dialog-bottom-transition" width="80%">
    <template v-slot:activator="{ on, attrs }">
      <v-container>
        <v-badge :value="!hasAlbum" color="warning">
          <v-btn class="button" v-bind="attrs" v-on="on"
            ><v-icon class="mr-2">mdi-album</v-icon>Album</v-btn
          >
        </v-badge>
      </v-container>
    </template>
    <template v-slot:default="dialog">
      <v-card height="600px" class="">
        <v-radio-group v-model="radios">
          <template v-slot:label>
            <v-card-title>
              <strong>Associated Albums</strong>
            </v-card-title>
          </template>

          <template v-slot:default="">
            <v-radio value="selectExisting">
              <template v-slot:label>
                <v-card-text>
                  Choose
                  <strong class="primary--text">EXISTING</strong> Album
                </v-card-text>
              </template>
            </v-radio>

            <v-radio value="createNew">
              <template v-slot:label>
                <v-card-text>
                  Create a <strong class="primary--text">NEW</strong> Album
                </v-card-text>
              </template>
            </v-radio>
          </template>
        </v-radio-group>

        <template>
          <v-autocomplete
            v-model="itemModel"
            label="Album"
            :items="items"
            item-text="title"
            item-value="id"
            class="selector"
            clearable
            return-object
            :disabled="radios === 'createNew'"
          >
            <template v-slot:no-data>
              <v-list-item> No Items Found... </v-list-item>
            </template>
          </v-autocomplete>
        </template>

        <v-text-field
          label="Album Title"
          v-model="albumTitle"
          :disabled="radios != 'createNew'"
        ></v-text-field>

        <v-text-field
          label="Release Date"
          v-model="releaseDate"
          :disabled="radios != 'createNew'"
        ></v-text-field>

        <v-spacer></v-spacer>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn class="button" @click="close"> Cancel </v-btn>
          <v-btn class="button" text @click="saveItemToDB"> Save </v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>
<script>
module.exports = {
  name: "AlbumSelectorRow",
  props: {
    items: Array,
    isEditing: Boolean,
    hasAlbum: Boolean,
    albumInfo: String,
  },
  emits: ["createAlbum", "selectAlbum"],
  data() {
    return {
      itemModel: null,
      choosingFromExisting: false,
      radios: "selectExisting",
      dialog: false,
      releaseDate: "",
      albumTitle: "",
    };
  },
  methods: {
    close() {
      this.dialog = false;
    },
    saveItemToDB() {
      if (this.radios === "createNew") {
        const args = {
          title: this.albumTitle,
          release_date: this.releaseDate,
        };
        console.log("Creating Album: ", args);
        this.$emit("createAlbum", args);
      } else {
        const args = {
          title: this.itemModel?.title,
        };
        console.log("Existing Album: ", args);
        this.$emit("selectAlbum", args);
      }

      this.close();
    },
  },
  created() {},
  computed: {},
};
</script>
<style></style>
