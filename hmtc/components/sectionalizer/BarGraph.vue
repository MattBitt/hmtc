<template>
  <div>
    <div id="fruit-meter">
      <div id="apples">200</div>
      <div id="bananas">5</div>
      <div id="peaches">10</div>
      <div id="apples">2</div>
      <div id="grapes">12</div>
    </div>
  </div>
</template>

<script>
module.exports = {
  name: "BarGraph",
  props: {},
  emits: [],
  data() {
    return {
      possibles: [],
    };
  },
  methods: {},
  created() {},
  computed: {},
};
</script>

<style>
#fruit-meter {
  border: 2px solid white;
  border-radius: 5px;
  overflow: hidden;
  display: grid;
  grid-template-columns: 20fr 5fr 10fr 2fr 12fr;
}

#apples {
  background: #48bb78;
}

#bananas {
  background: #ecc94b;
}

#peaches {
  background: #ed8936;
}

#cherries {
  background: #e53e3e;
}

#grapes {
  background: #805ad5;
}
</style>
