<template>
  <div>
    <MyToolTipChip
      icon="mdi-screw-flat-top"
      message="Hello,"
      myclass="ma-6"
      @myclicked="showMessage"
    />
    <MyToolTipChip
      icon="mdi-account"
      message="GoodBye,"
      myclass="mx-1"
      @myclicked="showMessage"
    />
  </div>
</template>
<script>
export default {
  methods: {
    showMessage(message) {
      console.log(message);
    },
  },
};
</script>
