<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      :close-on-content-click="true"
      :nudge-width="100"
      offset-x
    >
      <template v-slot:activator="{ on }">
        <v-btn class="button" v-on="on">
          {{ caption }}
        </v-btn>
      </template>

      <v-card>
        <v-container class="fill-height">
          <v-row class="no-gutters flex-wrap flex-column fill-height">
            <v-col cols="auto" class="grow pa-2">
              <v-btn
                v-for="(item, index) in items"
                :key="index"
                class="button ma-1 pa-1"
                @click="on_click(item)"
                >{{ item.title }}
              </v-btn>
            </v-col>
            <v-col cols="auto" class="footer shrink pa-2">
              Some Important Status
            </v-col>
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
.footer {
  background-color: var(--light);
  color: var(--on-light);
}
</style>
