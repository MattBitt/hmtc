<template>
  <v-autocomplete
    v-model="model"
    :items="items"
    :item-text="itemText"
    :filter="customFilter"
    :search-input.sync="searchQ"
    :item-value="itemValue"
    :label="label"
    :placeholder="placeholder || ''"
    :prepend-icon="icon"
    @input="selectionChanged"
    clearable
    @click:clear="clearItem"
    :disabled="!isEditing"
    return-object
  >
    <template v-slot:no-data>
      <v-list-item>
        <v-list-item-title>
          <v-btn @click="addNewItem" class="button"
            >Add new {{ label }} {{ searchString }}</v-btn
          >
        </v-list-item-title>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>
<script>
module.exports = {
  name: "SectionTopicsPanel",
  props: {
    value: String,
    label: String,
    items: Array,
    selectedItem: Object,
    isEditing: Boolean,
    itemText: String,
    itemValue: String,
    customFilter: Function,
    placeholder: String,
    icon: String,
  },
  emits: ["addNewItem", "selectItem", "clearItem"],
  methods: {
    selectionChanged() {
      this.$emit("selectItem", this.model);
    },
    addNewItem() {
      // notsure how to get the typed text here to add
      console.log(this.searchQ);
      this.$emit("addNewItem", this.searchString);
    },
    clearItem() {
      this.$emit("clearItem", this.model);
    },
  },
  data() {
    return {
      model: { id: 1, title: "Mizzle" },
      searchQ: null,
      searchString: "",
    };
  },
  watch: {
    searchQ(val) {
      if (val.length > 2 && val != this.model?.title) {
        this.searchString = val;
        // console.log("searching for", val);
      }
    },
  },
  mounted() {
    this.model = this.value;
    console.log("mounted", this.model, this.value);
  },
};
</script>
