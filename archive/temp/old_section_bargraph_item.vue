<template>
  <v-card class="text-center" :color="color" dark>
    <v-chip> Chip </v-chip>
    <v-card-text>
      <v-sheet color="rgba(0, 0, 0, .12)">
        <v-text-field label="Label"></v-text-field>
      </v-sheet>
    </v-card-text>

    <v-card-text>
      <h1 class="solara-some-class">
        {{ caption }}
      </h1>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions class="justify-center">
      <v-btn @click="test_logger"> Go to Report </v-btn>
    </v-card-actions>
  </v-card>
</template>

<style id="mycard">
.solara-some-class {
  font-weight: lighter;
}
</style>

<script>
export default {
  data: () => ({
    value: [],
  }),
  mounted: () => {
    console.log("mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {
    value: function (val) {
      console.log("value changed to", val);
    },
  },
};
</script>

<script type="text/javascript">
(function ($) {
  window.fnames = new Array();
  window.ftypes = new Array();
  fnames[0] = "EMAIL";
  ftypes[0] = "email";
  fnames[1] = "FNAME";
  ftypes[1] = "text";
  fnames[2] = "LNAME";
  ftypes[2] = "text";
  fnames[7] = "COMPANY";
  ftypes[7] = "text";
  fnames[10] = "WHYCLOUD";
  ftypes[10] = "text";
  fnames[3] = "ADDRESS";
  ftypes[3] = "address";
  fnames[4] = "PHONE";
  ftypes[4] = "phone";
  fnames[5] = "BIRTHDAY";
  ftypes[5] = "birthday";
  fnames[6] = "USECASE";
  ftypes[6] = "text";
  fnames[8] = "POSITION";
  ftypes[8] = "text";
  fnames[9] = "MMERGE9";
  ftypes[9] = "text";
})(jQuery);
var $mcj = jQuery.noConflict(true);
</script>
