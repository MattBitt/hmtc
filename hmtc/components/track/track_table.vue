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
      item-key="id"
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
            <!-- <template v-slot:activator="{ on, attrs }">
              <v-btn class="mb-2 button" v-bind="attrs" v-on="on">
                New Item
              </v-btn>
            </template> -->
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.title"
                        label="Name"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.album_id"
                        label="Album ID"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.video_id"
                        label="Video ID"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.track_number"
                        label="Track Number"
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
      <template v-slot:item.album_title="{ item }">
        <span v-if="item.album_title == null">---</span>
        <span v-else>{{ item.album_title }}</span>
      </template>
      <template v-slot:item.files="{ item }">
        <v-chip color="success" v-if="item.files.length == 2">
          <span><v-icon>mdi-check</v-icon> </span>
        </v-chip>
        <v-chip color="error" v-else>
          <span><v-icon>mdi-close</v-icon> ({{ item.files.length }})</span>
        </v-chip>
      </template>
      <template v-slot:item.jellyfin_id="{ item }">
        <span v-if="item.jellyfin_id == null">
          <v-chip color="error">
            <v-icon>mdi-close</v-icon>
          </v-chip>
        </span>
        <span v-else>
          <v-chip color="success"><v-icon>mdi-check</v-icon></v-chip>
        </span>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon
          x-large
          color="primary"
          class="mb-4"
          @click="link2_clicked(item.album_id)"
        >
          mdi-album
        </v-icon>
        <v-icon
          x-large
          color="primary"
          class="mb-4"
          @click="link1_clicked(item.section.video_id)"
        >
          mdi-rhombus-split
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
    sortBy: "title",
    sortDesc: true,
    search: "",
    headers: [
      {
        text: "ID",
        value: "id",
        filterable: true,
        sortable: true,
        width: "5%",
      },
      {
        text: "Track Number",
        value: "track_number",
        filterable: true,
        width: "5%",
      },
      {
        text: "Title",
        value: "title",
        align: "start",
        width: "20%",
      },
      { text: "Album", value: "album_title", filterable: false },
      { text: "Files", value: "files", filterable: false, sortable: true },
      {
        text: "JF ID",
        value: "jellyfin_id",
        filterable: true,
        sortable: true,
      },

      { text: "Actions", value: "actions", sortable: false },
    ],

    items: [
      {
        title: "Track Name",
        album_id: "",
        album_title: "",
        video_title: "",
        track_number: 0,
        video_id: true,
        id: 1168487,
      },
    ],

    editedIndex: -1,
    editedItem: {
      title: "Track Name",
      album_id: "",
      video_id: true,
      album_title: "",
      video_title: "",
      track_number: 0,
      id: -1,
    },
    defaultItem: {
      title: "Track Name",
      album_id: "",
      video_id: true,
      album_title: "",
      video_title: "",
      track_number: 0,
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

      this.dialog = true;
    },

    deleteItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },

    deleteItemConfirm() {
      this.items.splice(this.editedIndex, 1);
      this.delete_track(this.editedItem);
      this.closeDelete();
      this.close();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_track({
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
