<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      :close-on-content-click="true"
      :nudge-width="100"
      offset-x
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn class="main_button" v-bind="attrs" v-on="on">
          {{ caption }}
        </v-btn>
      </template>

      <v-card>
        <v-container>
          <v-flex
            flex-wrap
            align-content-space-between
            bg-surface-variant
            v-for="(item, index) in items"
            :key="index"
          >
            <v-btn class="button" v-bind="attrs" @click="on_click(item)"
              >{{ item.title }}
            </v-btn>
          </v-flex>
        </v-container>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text>Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
export default {
  data: () => ({
    caption: "Click Me!",
    items: [
      { id: 1, name: "Omegle Bars" },
      { id: 1, name: "Guerilla Bars" },
      { id: 1, name: "Livestreams" },
    ],
  }),
};
</script>
<style scoped>
.button {
  text-decoration: none;
  font-weight: 600;
  color: var(--whiteish) !important;
  background-color: var(--primary) !important;
}
.main_button {
  margin: 0.5em;
  padding: 0.25em 1em;
  text-decoration: none;
  font-weight: 800;
  color: var(--whiteish) !important;
  background-color: var(--primary) !important;
}
</style>
