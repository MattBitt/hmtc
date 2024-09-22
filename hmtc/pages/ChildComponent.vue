<template>
  <div>
    <p>{{ message }}</p>
  </div>
</template>

<script>
module.exports = {
  name: "ChildComponent",
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
