<template>
  <v-container class="pl-10">
    <v-row v-for="(name, index) in names" :key="index">
      <v-col cols="12">
        <v-text-field
          v-model="name.firstName"
          outlined
          dense
          solo
          :rules="rulesRequired"
        />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model="name.lastName"
          outlined
          dense
          solo
          :rules="rulesRequired"
        />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model="name.age"
          outlined
          dense
          solo
          :rules="rulesRequired"
        />
      </v-col>
      <v-btn
        type="submit"
        @click="submitForm(name.firstName, name.lastName, index)"
      >
        Submit
      </v-btn>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "playground",
  data: () => ({
    validForm: true,
    names: [
      {
        firstName: "john",
        lastName: "doe",
        age: 40,
      },
      {
        firstName: "jack",
        lastName: "",
        age: 30,
      },
    ],
    rulesRequired: [(v) => !!v || "Required"],
  }),
  methods: {
    submitForm(firstName, lastName, index) {
      console.log("Form submitted", index, firstName, lastName);
      this.validForm = true;
      this.names.forEach((name) => {
        if (!name.firstName || !name.lastName || !name.age) {
          this.validForm = false;
        }
      });
      if (this.validForm) {
        console.log("Form is valid");
      } else {
        console.log("Form is invalid");
      }
    },
  },
};
</script>
