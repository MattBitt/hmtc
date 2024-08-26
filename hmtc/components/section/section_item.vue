<template>
  <div class="outer-border">
    <v-container class="bg-surface-variant">
      <!-- Timer Display -->
      <v-row class="timer-row">
        <!-- Hours Digit -->


        <v-div class="placeholder digit">
          <v-col v-if="editing === true">
            <v-text-field class="digit-input" type="number" ref="input" :rules="[numberRule]"
              v-model.number="number1"></v-text-field>
          </v-col>
          <v-col v-else>
            {{ section.start_string.slice(0, 2) }}
          </v-col>
        </v-div>

        <div class="digit">
          <!-- Minutes Digit -->
          <v-col v-if="editing === true">
            <v-text-field class="digit-input" type="number" ref="input" :rules="[numberRule]"
              v-model.number="number2"></v-text-field>

          </v-col>
          <v-col v-else>
            {{ section.start_string.slice(3, 5) }}
          </v-col>
        </div>

        <!-- Seconds Digit -->
        <v-col v-if="editing === true">
          <div class="digit">

            <v-text-field class="digit-input" type="number" ref="input" :rules="[numberRule]"
              v-model.number="number3"></v-text-field>
          </div>
        </v-col>
        <v-col v-else>
          <div class="digit">

            {{ section.start_string.slice(6, 8) }}

          </div>
        </v-col>
      </v-row>

      <v-row class="button-row">
        <v-btn x-small @click="start_large_rewind()">
          <v-icon>mdi-step-backward-2</v-icon>
        </v-btn>
        <v-btn x-small @click="start_small_rewind()">
          <v-icon>mdi-step-backward</v-icon>
        </v-btn>
        <v-btn x-small @click="setEditMode()">
          <v-icon> mdi-pencil </v-icon>
        </v-btn>
        <v-btn x-small @click="start_small_forward()">
          <v-icon> mdi-step-forward </v-icon>
        </v-btn>
        <v-btn x-small @click="start_large_forward()">
          <v-icon left> mdi-step-forward-2 </v-icon>
        </v-btn>
      </v-row>
    </v-container>

    <v-container>
      <v-row>
        <v-text>{{ section.id }}</v-text>
      </v-row>
      <v-row>
        <v-text>{{ section.section_type }}</v-text>
      </v-row>
    </v-container>
    <v-container>
      <v-row class="section-info">
        <div>
          <v-btn @click="set_section_type('intro')">Intro</v-btn>
          <v-btn @click="set_section_type('instrumental')">Instrumental</v-btn>
          <v-btn @click="set_section_type('acapella')">Acapella</v-btn>
          <v-btn @click="set_section_type('outro')">Outro</v-btn>
        </div>
        <div>
          <v-btn @click="set_start_time('Settings Start time to asdf', 'start')">Set Start Time</v-btn>
          <v-btn @click="set_end_time('Settings End time to something else', 'end')">Set End Time</v-btn>
        </div>
      </v-row>
    </v-container>
  </div>
</template>
<style>
.digit {
  font-family: "Digital-7 Mono", sans-serif;
  width: 500px;
  font-size: 40px;
  font-weight: bolder;
  text-align: center;
  border: 4px solid #ee561e;
  color: #ff0f0c !important;
  box-sizing: border-box;
}

.digit-input input[type="number"] {
  -moz-appearance: textfield;
  color: #f6ff00 !important;
  background-color: #0f0f0f !important;
  text-align: center;
  width: 100px;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
}

.digit input::-webkit-outer-spin-button,
.digit input::-webkit-inner-spin-button {
  -webkit-appearance: none;
}

.outer-border {
  border: 4px double #0f0ffe;
  background-color: #f0f0f0;
}

.timer-row {
  border: 1px solid #af0fbb;
}

.button-row {
  border: 1px solid #21ba38;
}

.placeholder {
  border: 4px solid #ff0f0c;
}
</style>

<script>
export default {
  data: () => ({
    section: {
      id: "Section 2",
      start: "Start 2",
      end: "End 2",
      is_first: false,
      is_last: false,
      section_type: "intro",
      start_string: "fdsa",
      end_string: "asdf",
      hour_digits: "04",
      minute_digits: "20",
      second_digits: "58",
    },
    number1: 15,
    number2: 23,
    number3: 38,
    mytext: "Initial",
    edit_mode: false,
    edit_mode_end: false,
    editing: false,
    number: 0,
    numberRule: (val) => {
      if (val < 0) return "Please enter a positive number";
      return true;
    },
  }),
  methods: {
    writeText() {
      this.mytext = "Hello World!";
    },
    setEditMode() {
      this.edit_mode = !this.edit_mode;
    },
  },
  mounted: () => {
    console.log("mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {},
};
</script>
