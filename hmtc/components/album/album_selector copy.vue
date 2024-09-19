<template>
  <div id="app">
    <v-app id="inspire">
      <v-card>
        <v-card-title class="headline font-weight-regular blue-grey white--text"
          >Create Request</v-card-title
        >
        <v-card-text>
          <v-layout wrap>
            <v-flex xs12 md12>
              <v-subheader class="pa-0">{{ album }}</v-subheader>
            </v-flex>
            <v-flex xs12 md12>
              <v-autocomplete
                v-model="album"
                :items="py_albums"
                label="Album"
                prepend-icon="mdi-album"
                clearable
              >
              </v-autocomplete>
            </v-flex>
            <v-flex xs3 md3>
              <v-autocomplete
                v-model="product"
                :items="products"
                label="Product"
                prepend-icon="work"
                chips
                color="blue"
                clearable
              >
              </v-autocomplete>
            </v-flex>
            <v-flex xs3 md3>
              <v-autocomplete
                v-model="category"
                :items="categories"
                label="Category"
                prepend-icon="category"
                color="green"
                full-width
                solo
                hint="Random set of categories"
                clearable
              >
              </v-autocomplete>
            </v-flex>
            <v-flex xs3 md3>
              <v-autocomplete
                v-model="purpose"
                :items="purposes"
                label="Purpose"
                prepend-icon="category"
                color="red"
                full-width
                solo
                hint="Based on the selected category"
                clearable
              >
              </v-autocomplete>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
      <v-card> </v-card>
    </v-app>
  </div>
</template>
<script>
// 9-18-24 just read something about arrow functions and how they are not good
// when using Vue. Something wrong with how 'this' is utilized.
// I think the below format is the way to go for now
export default {
  data() {
    return {
      album: null,
      model: null,
      product: null,
      category: null,
      purpose: null,
      products: [
        "Samson",
        "Wichita",
        "Combustion",
        "Triton",
        "Helios",
        "Wimbeldon",
        "Brixton",
        "Iguana",
        "Xeon",
        "Falsy",
        "Armagedon",
        "Zepellin",
      ],
      categoriesPurposes: {
        FarmAnimals: ["cow", "sheep", "hen"],
        Directions: ["left", "right", "up", "down"],
        Time: ["past", "present", "future"],
        Element: ["air", "water", "tierra", "fire"],
      },
    };
  },
  computed: {
    categories() {
      console.log(Object.keys(this.categoriesPurposes));
      return Object.keys(this.categoriesPurposes);
    },
    purposes() {
      if (!this.category) {
        return null;
      } else {
        return this.categoriesPurposes[this.category];
      }
    },
    albums00() {
      if (!this.albums_raw) {
        return null;
      } else {
        return this.albums_raw.map((v) => v.toLowerCase());
      }
    },
  },
  watch: {
    filter() {
      this.searchedItems = this.$refs["selectExample"]?.filteredItems;
    },
  },
};
</script>
