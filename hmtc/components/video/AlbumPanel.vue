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
      <v-card max-height="90%" class="overflow-hidden">
        <v-row justify="center">
          <v-col cols="8">
            <v-radio-group v-model="radios" @change="resetValidation">
              <template v-slot:label>
                <v-card-title>
                  <div><strong>Albums</strong></div>
                </v-card-title>
                <v-card-text>
                  Choose to create a new album or select an existing one
                </v-card-text>
              </template>

              <template v-slot:default="">
                <v-radio value="createNew">
                  <template v-slot:label>
                    <v-card-text>
                      Create a <strong class="primary--text">NEW</strong> Album
                    </v-card-text>
                  </template>
                </v-radio>

                <v-radio value="selectExisting">
                  <template v-slot:label>
                    <v-card-text>
                      Choose
                      <strong class="primary--text">EXISTING</strong> Album
                    </v-card-text>
                  </template>
                </v-radio>
              </template>
            </v-radio-group>
          </v-col>
        </v-row>
        <v-form ref="myform" v-model="valid">
          <v-row justify="center">
            <v-col cols="6">
              <v-text-field
                v-model="albumTitle"
                :rules="radios === 'createNew' ? nameRules : []"
                :disabled="radios === 'selectExisting'"
                label="Album Title"
                required
              ></v-text-field>

              <v-text-field
                v-model="releaseDate"
                :rules="radios === 'createNew' ? releaseDateRules : []"
                :disabled="radios === 'selectExisting'"
                label="Release Date"
              ></v-text-field>

              <v-autocomplete
                v-model="itemModel"
                label="Album"
                :items="items"
                item-text="title"
                item-value="id"
                class="selector"
                clearable
                :rules="radios === 'selectExisting' ? itemSelectRules : []"
                :disabled="radios === 'createNew'"
                return-object
              >
                <template v-slot:no-data>
                  <v-list-item> No Items Found... </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>
          <v-card-actions>
            <v-btn class="button" @click="removeAlbum" :disabled="!hasAlbum">
              Remove
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn class="button" @click="close"> Cancel </v-btn>
            <v-btn class="button" :disabled="!valid" @click="saveItemToDB">
              Save
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </template>
  </v-dialog>
</template>
<script>
module.exports = {
  name: "AlbumSelectorRow",
  props: {
    items: Array,
    hasAlbum: Boolean,
    albumInfo: Object,
    possibleAlbumTitle: String,
  },
  emits: ["createAlbum", "selectAlbum", "removeAlbum"],
  data() {
    return {
      itemModel: null,
      radios: "",
      valid: true,
      dialog: false,
      releaseDate: "",
      albumTitle: this.possibleAlbumTitle || "",
      name: "",
      nameRules: [(v) => !!v || "Title is required"],
      releaseDate: "",
      releaseDateRules: [(v) => !!v || "Release Date is required"],
      select: null,
      itemSelectRules: [(v) => !!v || "Item is required"],
    };
  },
  methods: {
    close() {
      this.resetValidation();
      this.reset();
      this.albumTitle = this.possibleAlbumTitle || "";
      this.dialog = false;
    },
    removeAlbum() {
      this.$emit("removeAlbum");
      this.close();
    },
    saveItemToDB(item) {
      if (this.radios === "createNew") {
        const args = {
          title: this.albumTitle,
          release_date: this.releaseDate,
        };
        this.$emit("createAlbum", args);
      } else {
        const args = {
          title: this.itemModel?.title,
        };

        this.$emit("selectAlbum", args);
      }
      this.close();
    },
    validate() {
      this.$refs.myform.validate();
    },
    reset() {
      this.$refs.myform.reset();
    },
    resetValidation() {
      this.$refs.myform.resetValidation();
    },
  },
  created() {
    if (this.hasAlbum) {
      this.radios = "selectExisting";
    } else {
      this.radios = "createNew";
    }
  },
  computed: {},
  watch: {},
};
</script>
<style></style>
