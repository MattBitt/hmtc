<template>
  <div>
    <h1>HI</h1>
    <v-dialog v-model="this.dialog" max-width="500px" persistent>
      <v-card>
        <v-card-title class="text-h5">{{ message }}</v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn class="button" @click="cancel">Cancel</v-btn>
          <v-btn class="button mywarning" outlined @click="ok">OK</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
module.exports = {
  name: "OkCancelDialog",
  props: {
    dialog: Boolean,
    message: String,
  },
  emits: [],
  data() {
    return {
      dialog: false,
    };
  },
  methods: {
    cancel() {
      this.dialog = false;
      this.pycancel();
    },
    ok() {
      this.dialog = false;
      this.pyok();
    },
  },
};
</script>
