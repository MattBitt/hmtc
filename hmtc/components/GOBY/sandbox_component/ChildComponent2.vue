<template>
  <h1>Child Component # 2 {{ message }}</h1>
</template>

<script>
module.exports = {
  name: "ChildComponent2",
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
