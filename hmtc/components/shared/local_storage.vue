<!-- https://py.cafe/maartenbreddels/solara-localstorage -->
<!-- haven't implemented yet, but looks like it could be really usefull -->
<template>
  <div>
    <div v-if="debug">
      <div>{{ key }}={{ value }}</div>
    </div>
    <div v-else style="display: none"></div>
  </div>
</template>
<script>
module.exports = {
  created() {
    if (this.debug) {
      console.log("localstorage: created for", this.key);
    }
    const initialValue = localStorage.getItem(this.key);
    if (initialValue !== null) {
      if (this.debug) {
        console.log(
          "found initial value for localStorage",
          this.key,
          "=",
          initialValue
        );
      }
      this.value = initialValue;
    } else {
      if (this.debug) {
        console.log("no initial value for localStorage", this.key);
      }
    }
  },
  watch: {
    value(v) {
      if (this.debug) {
        console.log("set value to", v);
      }
      localStorage.setItem(this.key, this.value);
    },
  },
};
</script>
