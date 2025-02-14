<template>
  <Transition :name="name" :mode="mode">
    <jupyter-widget
      v-if="show_first && children.length > 0"
      :widget="children[0]"
      key="first-widget"
    ></jupyter-widget>
    <jupyter-widget
      v-if="!show_first && children.length > 1"
      :widget="children[1]"
      key="second-widget"
    ></jupyter-widget>
  </Transition>
</template>
<script>
module.exports = {
  name: "SwapTransition",
  props: {
    show_first: {
      type: Boolean,
      default: true,
    },
    children: {
      type: Array,
      default: [],
    },
    name: {
      type: String,
      default: "fade",
    },
    mode: {
      type: String,
      default: "out-in",
    },
  },
  emits: [],
  data() {
    return {};
  },
  methods: {},
  created() {},
  computed: {},
};
</script>
<style>
/* name="fade" */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* name="slide-fade" */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.8s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
