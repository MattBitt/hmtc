<template>
  <div>
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
      <template v-slot:item.release_date="{ item }">
        <v-chip color="info">{{ item.release_date }}</v-chip>
      </template>
      <template v-slot:item.title="{ item }">
        <span>{{ item.title }}</span>
      </template>
    </v-data-table>
  </div>
</template>
<script>
module.exports = {
  name: "VideoSelector",
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
