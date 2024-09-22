<template>
  <v-app>
    <v-row>
      <v-btn dark color="red" class="mt-6" @click="showMessage">Click Me</v-btn>
      <v-btn
        :dark="interactivities.length === 0"
        color="blue"
        class="mt-6 ml-3"
        @click="showInteractivity"
        :disabled="interactivities.length > 0"
        >Show Interactivity</v-btn
      >
      <v-btn dark color="green" class="mt-6 ml-3" @click="addObject()"
        >Random Toast</v-btn
      >
      <v-snackbar
        :messages.sync="messages"
        color="red"
        bottom
        left
      ></v-snackbar>
      <v-snackbar
        :messages.sync="interactivities"
        color="blue"
        :timeout="-1"
        bottom
        right
      >
        <template v-slot:action="{ close, message }">
          <div
            style="width: 76px"
            class="text-center"
            v-if="message.startsWith('Sending')"
          >
            <v-progress-circular
              indeterminate
              :width="2"
              :size="25"
            ></v-progress-circular>
          </div>
          <v-btn text @click="close()" v-else>Close</v-btn>
        </template>
      </v-snackbar>
      <v-snackbar :objects.sync="objects"></v-snackbar>
    </v-row>
  </v-app>
</template>

<script>
export default {
  name: "App",
  data: () => ({
    messages: [],
    interactivities: [],
    indexText: 0,
    randomText: [
      "Lorem ipsum dolor sit amet",
      "this is a very long text to show how the toast will handle this special case when the content is very long and shows on more than 1 line",
      "consectetur adipiscing elit",
      "sed do eiusmod tempor",
      "incididunt ut labore et dolore",
      "magna aliqua",
      "Turpis massa tincidunt",
      "dui ut ornare",
      "Tempor nec feugiat nisl",
      "pretium fusce id velit",
      "At imperdiet dui accumsan sit",
      "Id volutpat lacus",
    ],
    objects: [],
    colors: [
      "red",
      "blue",
      "green",
      "purple",
      "pink",
      "brown",
      "blue-grey",
      "orange",
      "lime",
      "cyan",
    ],
    transitions: ["fab-transition", "scale-transition", "fade-transition"],
  }),
  methods: {
    showMessage() {
      if (this.indexText >= this.randomText.length) this.indexText = 0;
      this.messages.push(this.randomText[this.indexText++]);
    },
    async showInteractivity() {
      this.interactivities.push("Sending email to Alice…");
      await this.timeout(1);
      this.interactivities.push("Sending email to Bob…");
      await this.timeout(2);
      this.$set(this.interactivities, 0, "Email sent to Alice!");
      // remove notification:
      setTimeout(() => this.interactivities.splice(0, 1), 3000);
      await this.timeout(5);
      this.$set(this.interactivities, 0, "Email sent to Bob!");
      // remove notification:
      setTimeout(() => this.interactivities.splice(0, 1), 2000);
    },
    addObject() {
      if (this.indexText >= this.randomText.length) this.indexText = 0;
      let randomColor = Math.floor(Math.random() * 11);
      let randomTransition = Math.floor(Math.random() * 3);
      let randomTop = Math.random() * 100;
      let randomLeft = Math.random() * 100;
      this.objects.push({
        message: this.randomText[this.indexText++],
        top: randomTop > 50,
        bottom: randomTop <= 50,
        left: randomLeft > 50,
        right: randomLeft <= 50,
        color: this.colors[randomColor],
        transition: this.transitions[randomTransition],
        timeout: Math.random() * 10000,
      });
    },
    timeout(delay) {
      return new Promise((res) => {
        setTimeout(res, delay * 1000);
      });
    },
  },
};
</script>
