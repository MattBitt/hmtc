<template>
  <h1>Child Component # 3 {{ message }}</h1>
</template>

<script>
module.exports = {
  name: "ANewComponent",
  props: {
    message: {
      type: String,
      required: true,
    },
  },
};
</script>

<style>
p {
  color: blue;
}
</style>
