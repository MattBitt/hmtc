<template>
  <div>
    <h1>Invite List</h1>
    >
    <form>
      <input type="text" placeholder="Enter name" v-model="nameInput" />
      <button @click.prevent="addName">Add Name</button>
    </form>

    <transition-group name="list" tag="ul">
      <li v-for="(name, index) in inviteList" :key="name">
        <button @click="uninvite(index)">X</button>
        {{ name }}
      </li>
    </transition-group>
  </div>
</template>
<script>
module.exports = {
  name: "EmptyComponent",
  props: {},
  emits: [],
  data() {
    return { inviteList: [], nameInput: "" };
  },
  methods: {
    addName() {
      this.inviteList.push(this.nameInput);
      this.nameInput = "";
    },
    uninvite(index) {
      this.inviteList.splice(index, 1);
    },
  },
  created() {},
  computed: {},
};
</script>
<style>
.list-move,
.list-enter-active,
.list-leave-active {
  transform: translateX(+50px);
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-50px);
}
.list-leave-active {
  position: absolute;
}
</style>
