<template>
  <v-row justify="center">
    <v-dialog v-model="dialog" max-width="800px" hide-overlay>
      <template v-slot:activator="{ on, attrs }">
        <v-badge :value="!hasYoutubeSeries" color="warning">
          <v-btn class="button" v-bind="attrs" v-on="on"
            ><v-icon class="mr-2">mdi-youtube</v-icon>Series</v-btn
          >
        </v-badge>
      </template>

      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>YoutubeSeries</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text :disabled="!valid" @click="saveItemToDB">
              Save
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>

        <v-card>
          <v-row>
            <v-spacer></v-spacer>
            <v-col cols="10">
              <div v-if="hasYoutubeSeries">
                <h4>Current:</h4>
                <strong>{{ youtubeseriesInfo?.title }}</strong>
                <v-btn color="warning" icon @click="removeYoutubeSeries">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </div>
              <v-list three-line subheader>
                <v-subheader
                  >Choose or create an YoutubeSeries for this video</v-subheader
                >
                <v-list-item>
                  <v-list-item-content>
                    <v-radio-group v-model="radios" @change="resetValidation">
                      <v-radio value="createNew">
                        <template v-slot:label>
                          <v-card-text>
                            Create a
                            <strong class="primary--text">NEW</strong>
                            YoutubeSeries
                          </v-card-text>
                        </template>
                      </v-radio>

                      <v-radio value="selectExisting">
                        <template v-slot:label>
                          <v-card-text>
                            Choose
                            <strong class="primary--text">EXISTING</strong>
                            YoutubeSeries
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
                              v-model="youtubeseriesTitle"
                              :rules="radios === 'createNew' ? nameRules : []"
                              :disabled="radios === 'selectExisting'"
                              label="YoutubeSeries Title"
                              required
                            ></v-text-field>
                          </v-list-item-content>
                        </v-list-item>
                        <v-list-item v-else>
                          <v-list-item-content>
                            <v-autocomplete
                              v-model="itemModel"
                              label="YoutubeSeries"
                              :items="items"
                              item-text="title"
                              item-value="id"
                              class="selector"
                              clearable
                              :rules="
                                radios === 'selectExisting'
                                  ? itemSelectRules
                                  : []
                              "
                              :disabled="radios === 'createNew'"
                              return-object
                              @click:clear="resetValidation"
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
              </v-list> </v-col
            ><v-spacer></v-spacer>
          </v-row>
        </v-card>

        <v-divider></v-divider>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script>
module.exports = {
  name: "YoutubeSeriesSelectorRow",
  props: {
    items: Array,
    hasYoutubeSeries: Boolean,
    youtubeseriesInfo: Object,
  },
  emits: ["createYoutubeSeries", "selectYoutubeSeries", "removeYoutubeSeries"],
  data() {
    return {
      itemModel: null,
      radios: "",
      valid: true,
      dialog: false,
      releaseDate: "",
      youtubeseriesTitle: "",
      name: "",
      nameRules: [(v) => !!v || "Title is required"],
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
      this.youtubeseriesTitle = "";
      this.dialog = false;
    },
    removeYoutubeSeries() {
      const args = {
        id: this.itemModel?.id,
        title: this.itemModel?.title,
      };
      this.$emit("removeYoutubeSeries", args);
      this.close();
    },
    saveItemToDB(item) {
      if (this.radios === "createNew") {
        const args = {
          title: this.youtubeseriesTitle,
          release_date: this.releaseDate,
        };
        this.$emit("createYoutubeSeries", args);
      } else {
        const args = {
          id: this.itemModel?.id,
          title: this.itemModel?.title,
        };

        this.$emit("selectYoutubeSeries", args);
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
    if (this.hasYoutubeSeries) {
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
