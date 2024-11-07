<template>
  <v-card>
    <v-card-title> </v-card-title>
    <v-data-table
      :headers="headers"
      :items="items"
      sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      :items-per-page="30"
      class="elevation-1"
      item-key="id"
    >
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Sections</v-toolbar-title>
          <v-divider class="mx-4" inset vertical></v-divider>
          <v-spacer></v-spacer>
          <v-dialog v-model="dialog" max-width="95%">
            <template v-slot:activator="{ on, attrs }">
              <v-btn class="button" v-bind="attrs" v-on="on"> New Item </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="3">
                      <span class="text-h5">ID: {{ editedItem.id }}</span>
                    </v-col>
                    <v-col cols="3">
                      <v-text-field
                        v-model="editedItem.start"
                        label="Start"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="3">
                      <v-text-field
                        v-model="editedItem.end"
                        label="End"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="3">
                      <v-text-field
                        v-model="editedItem.section_type"
                        label="Section Type"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="6">
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="adjustStartToCurrent()">
                          Sync Start to Jellyfin
                        </v-btn>
                      </v-row>
                      <v-row justify="center" class="mb-6">
                        <span class="seven-seg">{{ startStringJS }}</span>
                      </v-row>
                      <v-row justify="center">
                        <v-btn xs class="button" @click="setStartTime(-5)">
                          -5
                        </v-btn>
                        <v-btn xs class="button" @click="setStartTime(-1)">
                          -1
                        </v-btn>
                        <v-btn xs class="button" @click="setStartTime(-0.25)">
                          -0.25
                        </v-btn>
                        <v-btn xs class="button" @click="setStartTime(+0.25)">
                          +0.25
                        </v-btn>
                        <v-btn xs class="button" @click="setStartTime(+1)">
                          +1
                        </v-btn>
                        <v-btn xs class="button" @click="setStartTime(+5)">
                          +5
                        </v-btn>
                      </v-row>
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="loopStartJellyfin()">
                          Play in Jellyfin
                        </v-btn>
                      </v-row>
                    </v-col>
                    <v-col cols="6">
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="adjustEndToCurrent()">
                          Jellyfin Time
                        </v-btn>
                      </v-row>
                      <v-row justify="center" class="mb-6">
                        <span class="seven-seg">{{ endStringJS }}</span>
                      </v-row>
                      <v-row justify="center">
                        <v-btn xs class="button" @click="setEndTime(-5)">
                          -5
                        </v-btn>
                        <v-btn xs class="button" @click="setEndTime(-1)">
                          -1
                        </v-btn>
                        <v-btn xs class="button" @click="setEndTime(-0.25)">
                          -0.25
                        </v-btn>
                        <v-btn xs class="button" @click="setEndTime(+0.25)">
                          +0.25
                        </v-btn>
                        <v-btn xs class="button" @click="setEndTime(+1)">
                          +1
                        </v-btn>
                        <v-btn xs class="button" @click="setEndTime(+5)">
                          +5
                        </v-btn>
                      </v-row>
                      <v-row justify="center" class="mb-6">
                        <v-btn class="button" @click="loopEndJellyfin()">
                          Play in Jellyfin
                        </v-btn>
                      </v-row>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn class="button" @click="close">Cancel</v-btn>
                <v-btn class="button" @click="saveItemToDB(editedItem)">
                  Save
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dialogDelete" max-width="500px">
            <v-card>
              <v-card-title class="text-h5"
                >Are you sure you want to delete this item?</v-card-title
              >
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn class="button" @click="closeDelete">Cancel</v-btn>
                <v-btn class="button" @click="deleteItemConfirm">OK</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon medium class="mr-2" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon medium color="red" @click="deleteItem(item)">
          mdi-delete
        </v-icon>
      </template>
      <template v-slot:no-data>
        <v-btn class="button" @click=""> Reset </v-btn>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    is_connected: false,
    has_active_session: false,
    current_position: 0,
    play_status: "STOPPED",
    dialog: false,
    dialogDelete: false,
    sortBy: "start",
    sortDesc: true,
    search: "",
    headers: [
      { text: "Start", value: "start", filterable: false },
      { text: "End", value: "end", filterable: false },
      { text: "Duration (s)", value: "duration", filterable: false },
      { text: "ID", value: "id", filterable: false },
      { text: "Start String", value: "start_string", filterable: false },
      { text: "End String", value: "end_string", filterable: false },
      {
        text: "Section Type",
        value: "section_type",
      },

      { text: "Actions", value: "actions", sortable: false, filterable: false },
    ],

    items: [
      {
        section_type: "INITIAL",
        start: 0,
        end: 0,
        id: 682148,
      },
    ],

    editedIndex: -1,
    editedItem: {
      section_type: "INITIAL",
      start: 0,
      end: 0,
      id: -1,
    },
    startStringJS: "00:00:00",
    endStringJS: "00:00:00",
    defaultItem: {
      section_type: "INITIAL",
      start: 0,
      end: 0,
      id: -1,
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Item" : "Edit Item";
    },
  },

  watch: {
    dialog(val) {
      val || this.close();
    },
    dialogDelete(val) {
      val || this.closeDelete();
    },
  },

  methods: {
    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.startStringJS = this.timeString(this.editedItem.start);
      this.endStringJS = this.timeString(this.editedItem.end);
      this.dialog = true;
    },

    deleteItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },

    deleteItemConfirm() {
      this.items.splice(this.editedIndex, 1);
      this.delete_section(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_section({
        item: item,
        editedItem: this.editedItem,
      });

      // update the array in the front end and close the dialog box
      this.save();
      this.close();
    },

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.items[this.editedIndex], this.editedItem);
      } else {
        this.items.push(this.editedItem);
      }
      this.close();
    },

    setStartTime(value) {
      if (this.editedItem.start + value * 1000 >= 0) {
        this.editedItem.start += value * 1000;
        this.startStringJS = this.timeString(this.editedItem.start);
      }
    },
    setEndTime(value) {
      this.editedItem.end += value * 1000;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
    timeString(value) {
      const date = new Date(null);
      date.setSeconds(value / 1000); // specify value for SECONDS here
      return date.toISOString().slice(11, 19);
    },
    loopStartJellyfin() {
      this.loop_jellyfin(this.editedItem.start);
    },
    // Jellyfin Looping delay defined below
    loopEndJellyfin() {
      this.loop_jellyfin(this.editedItem.end - 1);
    },

    adjustStartToCurrent() {
      // this doesn't work since current_postion doesn't change
      // need to call it from python
      this.editedItem.start = this.current_position;
      this.startStringJS = this.timeString(this.editedItem.start);
    },

    adjustEndToCurrent() {
      this.editedItem.end = this.current_position;
      this.endStringJS = this.timeString(this.editedItem.end);
    },
  },
};
</script>
<style>
.seven-seg {
  font-family: "mySevenSegDisplay";
  font-size: 3em;
  color: var(--primary) !important;
  margin: 10px;
}
</style>
