<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="items"
      sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      :search="search"
      :items-per-page="30"
      class="elevation-1"
      item-key="name"
    >
      <template v-slot:top="{ pagination, options, updateOptions }">
        <v-toolbar flat>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
          <v-spacer></v-spacer>
          <v-data-footer
            :pagination="pagination"
            :options="options"
            @update:options="updateOptions"
            items-per-page-text="$vuetify.dataTable.itemsPerPageText"
          />

          <v-dialog v-model="dialog" max-width="800px">
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.start"
                        label="Start (ms)"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.end"
                        label="End (ms)"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.section_type"
                      label="Section Type"
                    ></v-text-field>
                  </v-col>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-btn
                  class="button mywarning"
                  outlined
                  @click="dialogDelete = true"
                >
                  <v-icon>mdi-delete</v-icon> Delete
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn class="button" @click="close"> Cancel </v-btn>
                <v-btn class="button" text @click="saveItemToDB(editedItem)">
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
                <v-btn
                  class="button mywarning"
                  outlined
                  @click="deleteItemConfirm"
                  >OK</v-btn
                >
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon
          x-large
          color="primary"
          class="mb-4"
          @click="link1_clicked(item)"
        >
          mdi-alpha
        </v-icon>
      </template>
      <template v-slot:no-data>
        <v-btn class="button" @click=""> Reset </v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    sortBy: "name",
    sortDesc: true,
    search: "",
    headers: [
      { text: "ID", value: "id", align: "start", width: "5%" },
      {
        text: "Start",
        value: "start_string",
        align: "center",
      },
      {
        text: "End",
        value: "end_string",
        align: "center",
      },
      {
        text: "Video ID",
        value: "video_id",
        filterable: true,
        sortable: true,
      },
      {
        text: "Section Type",
        value: "section_type",
        filterable: false,
        sortable: true,
      },

      { text: "Actions", value: "actions", sortable: false },
    ],

    items: [
      {
        text: "Topic Text",
        id: 1665436,
      },
    ],

    editedIndex: -1,
    editedItem: {
      text: "Topic Text",
      id: 1665436,
    },
    defaultItem: {
      text: "Topic Text",
      id: 1665436,
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
    toggleOrder() {
      this.sortDesc = !this.sortDesc;
    },
    nextSort() {
      let index = this.headers.findIndex((h) => h.value === this.sortBy);
      index = (index + 1) % this.headers.length;
      this.sortBy = this.headers[index].value;
    },

    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);

      this.dialog = true;
    },

    deleteItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },

    deleteItemConfirm() {
      this.items.splice(this.editedIndex, 1);
      this.delete_topic(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_topic({
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
  },
};
</script>
<style>
/* removes the items per page selector (doesn't work to display none)*/
.v-application--is-ltr .v-data-footer__pagination {
  margin-left: auto;
}
</style>
