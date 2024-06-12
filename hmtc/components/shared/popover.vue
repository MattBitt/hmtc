<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      :close-on-content-click="true"
      :nudge-width="100"
      offset-x
    >
      <template v-slot:activator="{ on }">
        <v-btn class="main_button" v-on="on">
          {{ caption }}
        </v-btn>
      </template>

      <v-card>
        <v-container class="fill-height">
          <v-row class="no-gutters flex-wrap flex-column fill-height">
            <v-col cols="auto" class="grow grey pa-2">
              <v-btn
                v-for="(item, index) in items"
                :key="index"
                class="button ma-2 pa-2"
                @click="on_click(item)"
                >{{ item.title }}
              </v-btn>
            </v-col>
            <v-col cols="auto" class="shrink blue pa-2"> Footer </v-col>
          </v-row>
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
    menu: false,
  }),
};
</script>
<style scoped>
.button {
  text-decoration: none;
  font-weight: 600;
  color: var(--whiteish) !important;
  background-color: var(--primary) !important;
  height: 40px !important;
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
