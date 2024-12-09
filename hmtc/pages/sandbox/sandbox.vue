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
        <v-toolbar flat>
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
          <v-spacer></v-spacer>
          <v-pagination
            v-model="current_page"
            :length="total_pages"
            :total-visible="6"
            @input="change_page"
          ></v-pagination>
        </v-toolbar>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon x-large color="primary" class="mb-4" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon x-large color="primary" class="mb-4" @click="action1(item)">
          {{ action1_icon }}
        </v-icon>
      </template>
    </v-data-table>
  </div>
</template>

<script>
module.exports = {
  name: "GoByTable",
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
      loading: false,
      options: {},
      search: "",
      filtered: false,
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
  },
};
</script>
