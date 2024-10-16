<template>
  <v-row justify="center">
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-badge :value="!hasAlbum" color="warning">
          <v-btn class="button" v-bind="attrs" v-on="on"
            ><v-icon class="mr-2">mdi-album</v-icon>Album</v-btn
          >
        </v-badge>
      </template>

      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Album</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text :disabled="!valid" @click="saveItemToDB">
              Save
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>

        <v-card>
          <v-list three-line subheader>
            <v-subheader>Choose or create an Album for this video</v-subheader>
            <v-list-item>
              <v-list-item-content>
                <v-radio-group v-model="radios" @change="resetValidation">
                  <v-radio value="createNew">
                    <template v-slot:label>
                      <v-card-text>
                        Create a
                        <strong class="primary--text">NEW</strong> Album
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
                </v-radio-group>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-form ref="myform" v-model="valid">
                  <v-list>
                    <v-list-item v-if="radios === 'createNew'">
                      <v-list-item-content>
                        <v-text-field
                          v-model="albumTitle"
                          :rules="radios === 'createNew' ? nameRules : []"
                          :disabled="radios === 'selectExisting'"
                          label="Album Title"
                          required
                        ></v-text-field>

                        <v-text-field
                          v-model="releaseDate"
                          :rules="
                            radios === 'createNew' ? releaseDateRules : []
                          "
                          :disabled="radios === 'selectExisting'"
                          label="Release Date"
                        ></v-text-field>
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item v-else>
                      <v-list-item-content>
                        <v-autocomplete
                          v-model="itemModel"
                          label="Album"
                          :items="items"
                          item-text="title"
                          item-value="id"
                          class="selector"
                          clearable
                          :rules="
                            radios === 'selectExisting' ? itemSelectRules : []
                          "
                          :disabled="radios === 'createNew'"
                          return-object
                        >
                          <template v-slot:no-data>
                            <v-list-item> No Items Found... </v-list-item>
                          </template>
                        </v-autocomplete>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-form>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>

        <v-divider></v-divider>
      </v-card>
    </v-dialog>
  </v-row>
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
      notifications: false,
      sound: true,
      widgets: false,
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
