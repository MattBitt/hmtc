<template>
  <div>
    <h1>Parent Component</h1>
    <MyChildComponent :message="myname" />
    <MyNextComponent iconName="mdi-video" :message="myname" />
    <div v-for="item in [1, 2, 3]" :key="item">
      <MyChildComponent :message="myname" />
    </div>
    <MyNextComponent :iconName="iconName" :message="myname" />
    <MyChildComponent :message="newName()" />
  </div>
</template>

<script>
module.exports = {
  name: "ParentComponent",
  props: {
    iconName: {
      type: String,
      required: true,
    },
    message: {
      type: String,
      required: false,
    },
  },
  methods: {
    newName() {
      return this.myname + this.myname;
    },
  },
};
</script>

<style>
h1 {
  color: green;
}
</style>
