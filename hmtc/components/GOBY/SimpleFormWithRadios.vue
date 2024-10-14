<!-- Check AlbumPanel for an updated version of this -->
<!-- the below may contain bugs 10/13/24 -->
<template>
  <div>
    <v-radio-group v-model="radios" @change="resetValidation">
      <template v-slot:label>
        <v-card-title>
          <strong>Simple Form</strong>
        </v-card-title>
      </template>

      <template v-slot:default="">
        <v-radio value="createNew">
          <template v-slot:label>
            <v-card-text>
              Create a <strong class="primary--text">NEW</strong> Album
            </v-card-text>
          </template>
        </v-radio>

        <v-radio value="selectExisting">
          <template v-slot:label>
            <v-card-text>
              Choose
              <strong class="primary--text">EXISTING</strong> Album
            </v-card-text>
          </template>
        </v-radio>
      </template>
    </v-radio-group>

    <v-form ref="myform" v-model="valid">
      <v-text-field
        v-model="name"
        :counter="10"
        :rules="radios === 'createNew' ? nameRules : []"
        :disabled="radios === 'selectExisting'"
        label="Name"
        required
      ></v-text-field>

      <v-text-field
        v-model="email"
        :rules="radios === 'createNew' ? emailRules : []"
        :disabled="radios === 'selectExisting'"
        label="E-mail"
        required
      ></v-text-field>

      <v-select
        v-model="select"
        :items="items"
        :rules="radios === 'selectExisting' ? itemSelectRules : []"
        :disabled="radios === 'createNew'"
        label="Item"
        clearable
        required
      ></v-select>

      <v-btn :disabled="!valid" color="success" class="mr-4" @click="validate">
        Validate
      </v-btn>

      <v-btn color="error" class="mr-4" @click="reset"> Reset Form </v-btn>

      <v-btn color="warning" @click="resetValidation"> Reset Validation </v-btn>
    </v-form>
  </div>
</template>
<script>
module.exports = {
  name: "EmptyComponent",
  props: {},
  emits: [],
  data() {
    return {
      radios: "createNew",
      valid: true,
      name: "",
      nameRules: [
        (v) => !!v || "Name is required",
        (v) => (v && v.length <= 10) || "Name must be less than 10 characters",
      ],
      email: "",
      emailRules: [
        (v) => !!v || "E-mail is required",
        (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
      ],
      select: null,
      items: ["Item 1", "Item 2", "Item 3", "Item 4"],
      itemSelectRules: [(v) => !!v || "Item is required"],
    };
  },
  methods: {
    validate() {
      console.log("Prevalidate");
      this.$refs.myform.validate();
      console.log("Post-validate");
      if (!this.valid) {
        console.log("DOes this ever happen?");
        return;
      }
      if (this.radios === "createNew") {
        console.log("Creating new item");
        const args = {
          name: this.name,
          email: this.email,
        };
        this.create_new(args);
      } else {
        console.log("Selecting existing item");
        const args = {
          album: this.select,
        };
        this.select_existing(args);
      }
    },
    reset() {
      this.$refs.myform.reset();
    },
    resetValidation() {
      this.$refs.myform.resetValidation();
    },
  },
  created() {},
  computed: {},
};
</script>
<style></style>
