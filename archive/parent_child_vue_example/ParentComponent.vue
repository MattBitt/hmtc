<template>
  <div>
    <h1>Parent Component</h1>
    <MyChildComponent :message="myname" />
  </div>
</template>

<script>
module.exports = {
  name: "ParentComponent",
};
computed = {
  myname() {
    return "John Doe";
  },
};
</script>

<style>
h1 {
  color: green;
}
</style>
