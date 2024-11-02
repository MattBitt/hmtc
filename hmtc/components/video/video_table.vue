<template>
  <!-- Main Data Table -->
  <v-data-table
    :headers="_headers"
    :items="items"
    sort-by.sync="sortBy"
    :sort-desc.sync="sortDesc"
    :search="search"
    :items-per-page="30"
    class="elevation-1"
    item-key="title"
    @pagination="writeLog"
    @click:row="handleClick"
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
        <v-divider inset vertical></v-divider>
        <v-data-footer
          :pagination="pagination"
          :options="options"
          @update:options="updateOptions"
          items-per-page-text="$vuetify.dataTable.itemsPerPageText"
        />
        <v-spacer></v-spacer>
        <!-- New/Edit Modal Dialog Starts Here -->
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
                      v-model="editedItem.title"
                      label="Title"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.duration"
                      label="Duration"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.episode"
                      label="Episode Number"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.youtube_id"
                      label="Youtube ID"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.jellyfin_id"
                      label="Jellyfin ID"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-text-field
                      v-model="editedItem.upload_date"
                      label="Upload Date"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" sm="6" md="4">
                    <v-checkbox
                      v-model="editedItem.contains_unique_content"
                      label="Unique Content"
                    ></v-checkbox>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn class="button" @click="close"> Cancel </v-btn>
              <v-btn class="button" text @click="saveItemToDB(editedItem)">
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <!-- Delete Dialog -->
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
    <!-- Custom cell contents for each column-->

    <template v-slot:item.upload_date="{ item }">
      <v-chip color="info">{{ item.upload_date }}</v-chip>
    </template>
    <template v-slot:item.title="{ item }">
      <span>{{ item.title }}</span>
    </template>
    <template v-slot:item.duration="{ item }">
      <v-chip color="info">{{
        new Date(item.duration * 1000).toISOString().substr(11, 8)
      }}</v-chip>
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
    <template v-slot:item.section_info.section_count="{ item }">
      <v-chip color="primary">{{ item.section_info.section_count }}</v-chip>
    </template>
    <template v-slot:item.file_count="{ item }">
      <span v-if="item.file_count == 6">
        <v-chip color="success">
          <v-icon>mdi-check</v-icon>
        </v-chip>
      </span>
      <span v-else-if="item.file_count == 0">
        <v-chip color="error">
          <v-icon>mdi-close</v-icon>
        </v-chip>
      </span>
      <span v-else>
        <v-chip color="warning">
          {{ item.file_count }}
        </v-chip>
      </span>
    </template>
    <template v-slot:item.section_info="{ item }">
      <div v-if="item.section_info.section_count <= 0">
        <v-chip color="warning">
          <v-icon>mdi-close</v-icon>
        </v-chip>
        <v-chip color="warning">
          <v-icon>mdi-close</v-icon>
        </v-chip>
      </div>
      <div v-else>
        <span
          v-if="
            item.section_info.section_count == item.section_info.track_count
          "
        >
          <v-chip color="success">
            <v-icon>mdi-check</v-icon>
          </v-chip>
        </span>
        <span v-else>
          <v-col class="text--center">
            <v-chip color="error">
              <span>
                {{ item.section_info.section_count }}
              </span>
              <span> / </span>
              <span>
                {{ item.section_info.track_count }}
              </span>
            </v-chip>
          </v-col>
        </span>

        <span>
          <v-chip color="success">
            {{ (item.section_info.my_new_column * 100).toFixed(2) }}%
          </v-chip>
        </span>
      </div>
    </template>
    <template v-slot:item.contains_unique_content="{ item }">
      <v-simple-checkbox
        v-model="item.contains_unique_content"
      ></v-simple-checkbox>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
        mdi-pencil
      </v-icon>
      <v-icon x-large color="primary" class="mb-4" @click="link1_clicked(item)">
        mdi-rhombus-split
      </v-icon>
    </template>
    <template v-slot:no-data>
      <v-btn class="button" @click=""> Reset </v-btn>
    </template>
  </v-data-table>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      sortBy: "title",
      sortDesc: true,
      search: "",
      headers: [
        {
          text: "Uploaded",
          value: "upload_date",
          filterable: false,
          width: "5%",
          align: "start",
        },

        {
          text: "Title",
          value: "title",
          width: "20%",
          align: "start",
        },
        {
          text: "Duration",
          value: "duration",
          filterable: false,
          sortable: true,
        },
        {
          text: "Sections",
          value: "section_info.section_count",
          filterable: false,
          sortable: true,
        },
        {
          text: "Files",
          value: "file_count",
          filterable: false,
          sortable: true,
        },

        {
          text: "Sectionilization",
          value: "section_info",
          filterable: false,
          width: "30%",
          sortable: false,
          align: "center",
        },
        {
          text: "JF ID",
          value: "jellyfin_id",
          filterable: true,
          sortable: true,
        },
        { text: "Unique", value: "contains_unique_content", filterable: false },
        {
          text: "",
          value: "actions",
          sortable: false,
          filterable: false,
          width: "5%",
          align: "end",
        },
      ],

      items: [
        {
          title: "Title 1",
          youtube_series_title: "Frozen Yogurt",
          episode: "",
          duration: 0,
          contains_unique_content: true,
          upload_date: "2021-01-01",
          id: 1,
          jellyfin_id: "",
        },
      ],

      editedIndex: -1,
      editedItem: {
        title: "Video Title",
        episode: "",
        duration: 0,
        contains_unique_content: true,
        upload_date: "",
        youtube_id: "",
        id: 0,
        jellyfin_id: "",
      },
      defaultItem: {
        title: "",
        episode: "",
        duration: 0,
        contains_unique_content: false,
        upload_date: "",
        youtube_id: "",
        id: 0,
        jellyfin_id: "",
      },
      expanded: [],
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Item" : "Edit Item";
    },

    _headers() {
      let h = this.headers;

      if (!this.show_nonunique) {
        h = h.filter((x) => x.value !== "contains_unique_content");
      }
      return h.filter((x) => !x.value.includes(this.hide_column));
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
      this.delete_video_item(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_video_item({
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
    writeLog() {
      console.log("Pagination event");
    },
    handleClick(item) {
      console.log(item);
    },
  },
};
</script>
<style>
.wrapclass {
  max-width: 99%;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
