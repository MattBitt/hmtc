<template>
  <div>
    <v-container class="bg-surface-variant mb-6">
      <v-row>
        <v-col cols="1">
          <v-sheet v-if="section.is_first === false">
            <v-btn @click="load_previous_section()">Prev</v-btn>
          </v-sheet>
        </v-col>
        <v-col cols="10">
          <v-sheet>
            <div class="align">
              <div class="seven-seg ma-4">
                {{ section.start_string }} - {{ section.end_string }}
              </div>

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
            </div>
          </v-sheet>
        </v-col>

        <v-col cols="1">
          <v-sheet v-if="section.is_last === false">
            <v-btn @click="load_next_section()">Next</v-btn>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>
<style>
.seven-seg {
  font-weight: bolder;
  font-size: 80px;
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
