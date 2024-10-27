<template>
  <v-row justify="center">
    <v-dialog
      v-model="dialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-badge :value="!hasSeries" color="warning">
          <v-btn class="button" v-bind="attrs" v-on="on"
            ><v-icon class="mr-2">mdi-shape</v-icon>Series</v-btn
          >
        </v-badge>
      </template>

      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Series</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text :disabled="!valid" @click="saveItemToDB">
              Save
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>

        <v-card>
          <v-row>
            <div v-if="hasSeries">
              <h4>Current:</h4>
              <strong>{{ seriesInfo?.name }}</strong>
              <v-btn color="warning" icon @click="removeSeries">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>

            <v-list three-line subheader>
              <v-subheader
                >Choose or create an Series for this video</v-subheader
              >
              <v-list-item>
                <v-list-item-content>
                  <v-radio-group v-model="radios" @change="resetValidation">
                    <v-radio value="createNew">
                      <template v-slot:label>
                        <v-card-text>
                          Create a
                          <strong class="primary--text">NEW</strong> Series
                        </v-card-text>
                      </template>
                    </v-radio>

                    <v-radio value="selectExisting">
                      <template v-slot:label>
                        <v-card-text>
                          Choose
                          <strong class="primary--text">EXISTING</strong> Series
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
                            v-model="seriesName"
                            :rules="radios === 'createNew' ? nameRules : []"
                            :disabled="radios === 'selectExisting'"
                            label="Series Name"
                            required
                          ></v-text-field>

                          <v-text-field
                            v-model="startDate"
                            :rules="
                              radios === 'createNew' ? startDateRules : []
                            "
                            :disabled="radios === 'selectExisting'"
                            label="Start Date"
                          ></v-text-field>

                          <v-text-field
                            v-model="endDate"
                            :rules="radios === 'createNew' ? endDateRules : []"
                            :disabled="radios === 'selectExisting'"
                            label="End Date"
                          ></v-text-field>
                        </v-list-item-content>
                      </v-list-item>
                      <v-list-item v-else>
                        <v-list-item-content>
                          <v-autocomplete
                            v-model="itemModel"
                            label="Series"
                            :items="items"
                            item-text="name"
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
          </v-row>
        </v-card>

        <v-divider></v-divider>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script>
module.exports = {
  name: "SeriesSelectorRow",
  props: {
    items: Array,
    hasSeries: Boolean,
    seriesInfo: Object,
  },
  emits: ["createSeries", "selectSeries", "removeSeries"],
  data() {
    return {
      itemModel: null,
      radios: "",
      valid: true,
      dialog: false,
      seriesName: "",
      name: "",
      nameRules: [(v) => !!v || "Name is required"],
      startDate: "",
      startDateRules: [],
      endDate: "",
      endDateRules: [],
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

      this.dialog = false;
    },
    removeSeries() {
      const args = {
        id: this.itemModel?.id,
        title: this.itemModel?.name,
      };
      this.$emit("removeSeries", args);
      this.close();
    },
    saveItemToDB(item) {
      if (this.radios === "createNew") {
        const args = {
          name: this.seriesName,
          start_date: this.startDate,
          end_date: this.endDate,
        };
        this.$emit("createSeries", args);
      } else {
        const args = {
          id: this.itemModel?.id,
          name: this.itemModel?.name,
        };

        this.$emit("selectSeries", args);
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
    if (this.hasSeries) {
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
