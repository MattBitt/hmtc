<!-- <template>
  <v-layout wrap>
    <v-flex xs6 md6>
      <v-subheader class="pa-0">Inital Item:{{ initialItem }}</v-subheader>
      <v-subheader class="pa-0">Selected Item:{{ selectedItem }}</v-subheader>
    </v-flex>
    <v-flex xs12 md12>
      <v-autocomplete
        v-model="selectedItem"
        :items="items"
        :label="label"
        :prepend-icon="icon"
        clearable
        return-object
        no-data-text="No matching items"
        @change="changeItem"
      >
      </v-autocomplete>
      <v-btn @click="saveItem(selectedItem)" :disabled="!is_dirty">Save</v-btn>
      <v-btn @click="cancel" :disabled="!is_dirty">Cancel</v-btn>
    </v-flex>
  </v-layout>
</template>

<script>
// 9-18-24 just read something about arrow functions and how they are not good
// when using Vue. Something wrong with how 'this' is utilized.
// I think the below format is the way to go for now
export default {
  data() {
    return {
      is_dirty: false,
      icon: "mdi-null",
      label: "nulllll",
      initialItem: null,
      selectedItem: null,
    };
  },
  methods: {
    changeItem() {
      console.log("changeItem");
      if (this.selectedItem !== this.initialItem) {
        this.is_dirty = true;
      } else {
        this.is_dirty = false;
      }
      console.log(this.selectedItem);
    },
    saveItem(item) {
      console.log("save_item");
      console.log(item);
      this.save_item(item);
    },
  },
  mounted() {
    this.initialItem = this.selectedItem;
  },
};
</script> -->
