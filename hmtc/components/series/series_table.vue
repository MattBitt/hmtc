<template>
  <v-card>
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
                        v-model="editedItem.name"
                        label="Name"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.start_date"
                        label="Start Date"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.end_date"
                        label="End Date"
                      ></v-text-field>
                    </v-col>
                  </v-row>
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
      <template v-slot:item.video_count="{ item }">
        <v-chip>
          <span v-if="item.video_count > 0">
            <a :href="'/videos/series/' + item.id">
              {{ item.video_count }}
            </a>
          </span>
          <span v-else>---</span>
        </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
          mdi-pencil
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
    dialog: false,
    dialogDelete: false,
    sortBy: "name",
    sortDesc: true,
    search: "",
    headers: [
      { text: "ID", value: "id", align: "start", width: "5%" },
      {
        text: "Name",
        value: "name",
        align: "start",
        width: "20%",
      },
      {
        text: "# Videos",
        value: "video_count",
        filterable: false,
        sortable: true,
      },
      {
        text: "# Youtube Series",
        value: "youtube_series_count",
        filterable: false,
        sortable: true,
      },
      { text: "Start Date", value: "start_date", filterable: true },
      { text: "End Date", value: "end_date", filterable: true },

      // { text: 'Unique', value: 'contains_unique_content', filterable: false },
      { text: "Actions", value: "actions", sortable: false },
    ],

    items: [
      {
        name: "Series Name",
        start_date: "2024-01-01",
        end_date: "2024-12-31",
        id: 1665436,
      },
    ],

    editedIndex: -1,
    editedItem: {
      name: "Series Name",
      start_date: "2024-01-01",
      end_date: "2024-12-31",
      id: 1665436,
    },
    defaultItem: {
      name: "Series Name",
      start_date: "2024-01-01",
      end_date: "2024-12-31",
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
      this.delete_series(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_series({
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
/* removes the items per page selector*/
.v-data-footer__select {
  display: none;
}
</style>
