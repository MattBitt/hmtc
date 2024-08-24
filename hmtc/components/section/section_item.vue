<template>
  <div>
    <v-container class="bg-surface-variant mb-6 mycard">
      <v-row>
        <v-col cols="12">
          <v-sheet>
            <v-btn @click="load_previous_section()">Prev</v-btn>
            <v-btn @click="load_next_section()">Next</v-btn>
          </v-sheet>

          <v-container>
            <v-row>
              <v-col>
                <v-row
                  v-if="edit_mode_end === true"
                  class="text-left"
                  justify="center"
                >
                  <v-col cols="6">
                    <v-row>
                      <v-text-field
                        class="number_edit"
                        type="number"
                        step="1"
                        min="0"
                        max="59"
                        ref="input"
                        :rules="[numberRule]"
                        v-model.number="number"
                      ></v-text-field>
                    </v-row>
                  </v-col>
                </v-row>
                <v-row v-else class="text-center" justify="center">
                  <v-col cols="6">
                    <v-row class="text-center" justify="center">
                      <div class="seven-seg ma-4">
                        {{ section.end_string.slice(0, 2) }}
                      </div>
                      <div class="seven-seg ma-4">
                        {{ section.end_string.slice(3, 5) }}
                      </div>
                      <div class="seven-seg ma-4">
                        {{ section.end_string.slice(6, 8) }}
                      </div>
                    </v-row>
                    <v-row class="text-center" justify="center">
                      <v-btn x-small @click="end_large_rewind()">
                        <v-icon>mdi-step-backward-2</v-icon>
                      </v-btn>
                      <v-btn x-small @click="end_small_rewind()">
                        <v-icon>mdi-step-backward</v-icon>
                      </v-btn>
                      <v-btn x-small @click="edit()">
                        <v-icon> mdi-pencil </v-icon>
                      </v-btn>
                      <v-btn x-small @click="end_small_forward()">
                        <v-icon> mdi-step-forward </v-icon>
                      </v-btn>
                      <v-btn x-small @click="end_large_forward()">
                        <v-icon left> mdi-step-forward-2 </v-icon>
                      </v-btn>
                    </v-row>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-container>

          <v-container>
            <v-row>
              <h4>{{ section.id }}</h4>
              <h4>{{ section.section_type }}</h4>

              <div class="mb-6">
                <v-btn @click="set_section_type('intro')">Intro</v-btn>
                <v-btn @click="set_section_type('instrumental')"
                  >Instrumental</v-btn
                >
                <v-btn @click="set_section_type('acapella')">Acapella</v-btn>
                <v-btn @click="set_section_type('outro')">Outro</v-btn>
              </div>
              <div class="mb-6">
                <v-btn @click="set_start_time('asdf')">Set Start Time</v-btn>
                <v-btn @click="set_end_time('fdsa')">Set End Time</v-btn>
              </div>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<style>
.seven-seg {
  font-weight: bolder;
  font-size: 40px;
  color: #ff0000;
  /* font-family: "Seven Segment", sans-serif; */
  font-family: "Digital-7 Mono", sans-serif;
}
.intro-text {
  font-size: 60px;
  font-weight: bold;
  font-family: cursive;
  color: #444;
}
.description-text {
  font-size: 19px;
  font-family: cursive;
  margin: 32px 0;
  color: #4444ba;
}

.mycard {
  background-color: #f0f0f0;
  border-radius: 10px;
  padding: 10px;
  margin: 10px;
}
.number_edit {
  max-width: 50px;
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
    },
    edit_mode_start: false,
    edit_mode_end: false,
    number: 0,
    numberRule: (val) => {
      if (val < 0) return "Please enter a positive number";
      return true;
    },
  }),
  methods: {},
  mounted: () => {
    console.log("mounted");
  },
  destroyed: () => {
    console.log("destroyed");
  },
  watch: {},
};
</script>
