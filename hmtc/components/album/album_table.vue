<template>
  <div>
    <!-- <MyFirst
      initialTitle="ssome crazy title"
      initialReleaseDate="2024-10-06"
      @myincrease="increaseCount"
    /> -->
    <v-card>
      <v-card-title>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
        <!-- <v-divider></v-divider>
        <h1>{{ computedMyCount }}</h1> -->
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="items"
        sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        :search="search"
        :items-per-page="30"
        class="elevation-1"
        item-key="id"
        @pagination="writeLog"
      >
        <template v-slot:top="{ pagination, options, updateOptions }">
          <v-data-footer
            :pagination="pagination"
            :options="options"
            @update:options="updateOptions"
            items-per-page-text="$vuetify.dataTable.itemsPerPageText"
          />
          <v-toolbar flat>
            <v-toolbar-title>Albums</v-toolbar-title>
            <v-divider class="mx-4" inset vertical></v-divider>
            <v-spacer></v-spacer>
            <v-dialog v-model="dialog" max-width="800px">
              <template v-slot:activator="{ on, attrs }">
                <v-btn class="mb-2 button" v-bind="attrs" v-on="on">
                  New Item
                </v-btn>
              </template>
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
                          v-model="editedItem.release_date"
                          label="Release Date"
                        ></v-text-field>
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
        <template v-slot:item.video_count="{ item }">
          <v-chip>
            <span v-if="item.video_count > 0">
              <a :href="'/videos/album/' + item.id">
                {{ item.video_count }}
              </a>
            </span>
            <span v-else>---</span>
          </v-chip>
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
  </div>
</template>

<script>
export default {
  data() {
    return {
      mycount: 0,
      dialog: false,
      dialogDelete: false,
      sortBy: "title",
      sortDesc: true,
      search: "",
      headers: [
        { text: "ID", value: "id", align: "start", width: "5%" },
        {
          text: "Title",
          value: "title",
          align: "start",
          width: "40%",
        },
        {
          text: "# Videos",
          value: "video_count",
          filterable: false,
          sortable: true,
        },

        {
          text: "Release Date",
          value: "release_date",
          filterable: false,
          width: "10%",
        },

        // { text: 'Unique', value: 'contains_unique_content', filterable: false },
        { text: "Actions", value: "actions", sortable: false },
      ],

      items: [
        {
          title: "Album Name",
          video_id: 0,
          release_date: "2021-01-01",
          id: 1168487,
        },
      ],

      title: "My First Title (again)",

      editedIndex: -1,
      editedItem: {
        title: "Album Name",
        video_id: 0,
        release_date: "2021-01-01",
        id: -1,
      },
      defaultItem: {
        title: "Album Name",
        video_id: 0,
        release_date: "2021-01-01",
        id: -1,
      },
    };
  },
  mounted() {},

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Item" : "Edit Item";
    },
    computedMyCount() {
      return this.mycount;
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
    getColor(duration) {
      if (duration < 60) return "red";
      else if (duration < 900) return "orange";
      else return "green";
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
      this.delete_album(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_album({
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
    writeLog(paginationObject) {
      // this is an example of intercepting the pagination event
      // to perform some action
      let action;
      //console.log(paginationObject);
      this.currentPage < paginationObject.page
        ? (action = "forward")
        : (action = "backguard");
      this.currentPage = paginationObject.page;
      //console.log(action);
      //Write code to call your backend using action...
    },
    increaseCount(title, releaseDate) {
      // console.log("increase count by", n, " ", this.mycount);
      // this.mycount += n;
      // console.log(title, releaseDate);
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
