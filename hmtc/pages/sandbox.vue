<template>
  <div id="app">
    <header>
      <transition name="slide" mode="out-in">
        <div v-if="count === 0">
          <h3>{{ message }}</h3>
          <button @click="startCountdown">Restart the Clock</button>
        </div>

        <h3 v-else>Counting...</h3>
      </transition>
    </header>
    <transition-group class="grid" name="slide">
      <div v-for="n in count + 1" class="card" :key="n">
        <!-- Transition as the count changes (note the key on the h1 element) -->

        <h1 :style="{ color: numberColor }">{{ n - 1 }}</h1>
      </div>
    </transition-group>
    <!-- Transition once the button and message enter the view -->
  </div>
</template>

<script>
export default {
  props: {
    start: {
      type: Number,
      default: 10,
      required: false,
    },
    lyrics: {
      type: Array,
      required: true,
      validator: (value) =>
        value.every((item) => "timestamp" in item && "text" in item),
    },
    currentTimestamp: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      count: "",
      message: "And we're done!",
      timer: null, // Tracks the setInterval timer
    };
  },
  computed: {
    numberColor() {
      if (this.count < this.start * 0.33) {
        return "var(--color-danger)";
      } else if (this.count < this.start * 0.66) {
        return "var(--color-warning)";
      } else {
        return "var(--color-success)";
      }
    },
  },
  mounted() {
    // When the Vue component mounts, start the countdown
    this.startCountdown();
  },
  methods: {
    // Handler within setInterval
    countDown() {
      if (this.count === 0) {
        clearInterval(this.timer);
      } else {
        this.count--;
      }
    },
    startCountdown() {
      this.count = this.start; //
      this.timer = setInterval(this.countDown, 750);
    },
  },
};
</script>

<!-- Use preprocessors via the lang attribute! e.g. <style lang="scss"> -->
<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@200;300;900&display=swap");
:root {
  --color-text: #2c3e50;
  --color-primary: #0496ff;

  --color-success: #2a9d8f;
  --color-warning: #e9c46a;
  --color-danger: #e76f51;
  --body-background: #f9f9f9;
}

#app {
  background: var(--body-background);
  font-family: "Poppins", Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: var(--color-text);
  padding-top: 60px;
  height: 100vh;
  width: 100vw;
}

header {
  border-bottom: 1px solid #ddd;
  height: 100px;
  margin: 0 0 30px;
  padding: 0 0 30px;
}

h1 {
  font-size: 4rem;
  transition: color 0.3s;
}

h3 {
  letter-spacing: 1px;
  text-transform: uppercase;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, 135px);
  gap: 1rem;
  margin: 1rem auto;
  padding: 0 2rem;
  max-width: 590px;
}

.card {
  box-shadow: rgba(17, 17, 26, 0.05) 0px 4px 16px,
    rgba(17, 17, 26, 0.05) 0px 8px 32px;
  border-radius: 25px;
  display: inline-flex;
  padding: 8px;
  height: 120px;
  width: 120px;
  align-items: center;
  justify-content: center;
}

button {
  color: var(--color-primary);
  background: none;
  border: solid 1px;
  border-radius: 2em;
  font: inherit;
  padding: 0.75em 2em;

  &:hover,
  &:focus {
    background: var(--color-primary);
    color: #fff;
    cursor: pointer;
  }
}

/* Transition Styles */
.scale-enter-active,
.scale-leave-active {
  transition: transform 0.3s;
}
.scale-enter {
  transform: scale(1.5);
}

.slide-enter-active,
.slide-leave-active {
  transition: opacity 0.8s, transform 0.8s;
}
.slide-enter,
.slide-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
