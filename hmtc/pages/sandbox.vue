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
            @click:clear="clear_search"
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
    </v-data-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: true,
      options: {},
      headers: [],
      search: "",
      items: [],
      filtered: false,
    };
  },
  watch: {
    options: {
      handler: _.debounce(function () {
        this.loadItems();
      }, 200),
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
            this.loading = true;
            this.filtered = true;
            this.search_for_item(this.search);
            this.loading = false;
          }
        }
      }, 300),
    },
  },
  methods: {
    loadItems() {
      this.loading = true;
      this.new_options(this.options);
      this.loading = false;
    },
  },
};
</script>
