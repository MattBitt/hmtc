<template>
  <v-container style="background-color: purple;">
    <!-- Timer Display -->
    <v-sheet>
      <v-row class="d-flex justify-center">
        <v-responsive max-width="500" class="mx-2 py-2">{{ section.id }} ({{ section_type }}) start={{ section.start }}
          end={{ section.end }}</v-responsive>
      </v-row>
      <v-row class="d-flex justify-center">{{ timestamp }} : {{ hour }} : {{ minute }} : {{ second }}</v-row>
      <v-row class="d-flex justify-center">
        <!-- Hours Digit -->
        <v-responsive max-width="50" class="mx-2 py-2">
          <v-text-field ref="input" v-model="timestamp.hour" class="digit-input"></v-text-field>
        </v-responsive>

        <!-- Minutes Digit -->
        <v-responsive max-width="50" class="mx-2 py-2">
          <v-text-field ref="input" v-model="timestamp.minute" class="digit-input"></v-text-field>

        </v-responsive>

        <!-- Seconds Digit -->
        <v-responsive max-width="50" class="mx-2 py-2">
          <v-text-field ref="input" v-model="timestamp.second" class="digit-input"></v-text-field>
        </v-responsive>
      </v-row>
      <v-row class="d-flex justify-center">
        <v-btn x-small class="button" @click="adjust_section('large_backward')"><v-icon>mdi-step-backward-2</v-icon>
        </v-btn>
        <v-btn x-small class="button" @click="adjust_section('small_backward')"><v-icon>mdi-step-backward-2</v-icon>
        </v-btn>
        <v-btn x-small class="button" @click="adjust_section('tiny_backward')"><v-icon>mdi-step-backward</v-icon>
        </v-btn>
        <v-btn x-small class="button" @click="adjust_section('tiny_forward')"><v-icon>mdi-step-forward</v-icon>
        </v-btn>
        <v-btn x-small class="button" @click="adjust_section('small_forward')"><v-icon>mdi-step-forward-2</v-icon>
        </v-btn>
        <v-btn x-small class="button" @click="adjust_section('large_forward')"><v-icon>mdi-step-forward-2</v-icon>
        </v-btn>
      </v-row>
      <v-row class="d-flex justify-center">
        <v-responsive max-width="200" class="mx-2 py-2">
          <v-btn class="button" @click="handle_save">Submit</v-btn>
        </v-responsive>
        <v-responsive max-width="200" class="mx-2 py-2">
          <v-btn class="button" @click="handle_close">Cancel</v-btn>
        </v-responsive>


      </v-row>
    </v-sheet>
  </v-container>
</template>
<style>
.digit-input {
  font-size: 30px;
  text-align: center;

}
</style>

<script>
export default {
  data: () => ({
    label: "Blank Text",
    section: "Blank Section",
    section_type: "Blank Section Type",
    timestamp: {
      id: 456,
      timestamp: 456,
      hour: 10,
      minute: 20,
      second: 30,
    },


  }),
  methods: {
    mymethod: () => {
      console.log("mymethod");
    },
    hour() {
      console.log(this.timestamp.timestamp);
      h = Math.floor(this.timestamp.timestamp / 3600);
      return String(h).padStart(2, "0");
    },
    minute() {
      t = this.timestamp.timestamp - this.hour() * 3600;
      m = Math.floor(t / 60);
      return String(m).padStart(2, "0");
    },
    second() {
      t = this.timestamp.timestamp - this.hour() * 3600 - this.minute() * 60;

      s = Math.floor(t);
      return String(s).padStart(2, "0");
    },

  },
  mounted: () => {
    console.log("mounted");

  },
  beforeDestroy: () => {
    console.log("beforeDestroy");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  beforeCreate: () => {
    console.log("beforeCreate");
  },
};
</script>

<style></style>