<template>
  <div>
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Edit Video {{ currentItem.id }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text :disabled="!valid" @click="saveItemToDB">
              Save
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.title"
                  label="Title"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.duration"
                  label="Duration"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.episode"
                  label="Episode Number"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.youtube_id"
                  label="Youtube ID"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.jellyfin_id"
                  label="Jellyfin ID"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="currentItem.upload_date"
                  label="Upload Date"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-checkbox
                  v-model="currentItem.unique_content"
                  label="Unique Content"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-btn class="button mywarning" @click="deleteItem"
            ><v-icon>mdi-delete</v-icon>Delete</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn class="button" @click="close"> Cancel </v-btn>
          <v-btn class="button" text @click="saveItemToDB"> Save </v-btn>
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
          <v-btn class="button mywarning" outlined @click="deleteItemConfirm"
            >OK</v-btn
          >
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-data-table
      :headers="headers"
      :items="items"
      :page.sync="current_page"
      :options.sync="options"
      :server-items-length="total_items"
      :search="search"
      :loading="loading"
      class="elevation-1"
    >
      <template v-slot:top="{ pagination, options, updateOptions }">
        <v-toolbar>
          <v-row>
            <v-col cols="4">
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
                clearable
                @click:append="search_for_item(search)"
                @click:clear="clear_search"
                @keyup.enter="search_for_item(search)"
              ></v-text-field>
            </v-col>

            <v-col cols="2">
              <span>Items {{ total_items }}</span>
            </v-col>

            <v-col cols="6">
              <v-pagination
                v-model="current_page"
                :length="total_pages"
                :total-visible="4"
                @input="change_page"
              ></v-pagination>
            </v-col>
          </v-row>
        </v-toolbar>
      </template>
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
        <span>
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
      <template v-slot:item.superchats="{ item }">
        <a :href="'/superchats/' + item.id">
          <v-chip color="info">{{ item.superchats_count }}</v-chip>
        </a>
      </template>
      <template v-slot:item.segments_count="{ item }">
        <a :href="'/superchat-segments/' + item.id">
          <v-chip color="info">{{ item.segments_count }}</v-chip>
        </a>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon x-large color="primary" class="mb-4" @click="action1(item)">
          {{ action1_icon }}
        </v-icon>
        <a :href="'/domains/superchat-control-panel/' + item.id">
          <v-icon x-large color="primary" class="mb-4"> mdi-comment </v-icon></a
        >
      </template>
    </v-data-table>
  </div>
</template>

<script>
module.exports = {
  name: "VideoTable",
  props: {
    items: Array,
    headers: Array,
    total_items: Number,
    total_pages: Number,
    action1_icon: String,
  },
  emits: [],
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      loading: false,
      options: {},
      search: "",
      filtered: false,
      currentItem: {},
      valid: false,
    };
  },
  watch: {
    options: {
      handler: _.debounce(function () {
        this.loadItems();
      }, 400),
      deep: true,
    },
    search: {
      handler: _.debounce(function () {
        if (this.search == null) {
          this.filtered = false;
        } else {
          if (this.filtered) {
            if (this.search.length < 1) {
              this.clear_search();
              this.filtered = false;
            }
          } else if (this.search.length > 2) {
            this.filtered = true;
            this.search_for_item(this.search);
          }
        }
      }, 400),
      deep: true,
    },
  },
  methods: {
    loadItems() {
      this.new_options(this.options);
    },
    editItem(item) {
      this.currentItem = Object.assign({}, item);
      this.dialog = true;
    },
    close() {
      this.dialog = false;
    },
    closeDelete() {
      this.dialogDelete = false;
    },
    saveItemToDB() {
      this.save_item(this.currentItem);
      this.loadItems();
      this.currentItem = {};
      this.close();
    },
    deleteItem(item) {
      this.dialogDelete = true;
    },
    deleteItemConfirm() {
      this.delete_item(this.currentItem);
      this.closeDelete();
      this.loadItems();
      this.close();
      this.currentItem = {};
    },
  },
};
</script>
<style>
/* removes the items per page selector*/
.v-data-footer {
  display: none;
}
</style>
