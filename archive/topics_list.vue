<template>

  <v-sheet class="mt-0 py-6">
    <v-item-group mandatory>
      <v-container>
        <v-row>
          <v-item v-for="topic in topics" v-slot="{ active, toggle }">
            <v-card :color="active ? 'primary' : ''" class="d-flex align-center mx-8 px-8" height="50" @click="toggle">
              <v-scroll-y-transition>
                <div class="text-h1 flex-grow-1 text-center">
                  {{ topic }}
                </div>
              </v-scroll-y-transition>
            </v-card>
          </v-item>

        </v-row>
      </v-container>
    </v-item-group>
  </v-sheet>

</template>
<style></style>
<script>

export default {

  data: () => ({
    topics: ["acoustic", "acapella", "psychedelic", "banana"],

    items: [
      {
        icon: 'mdi-wifi',
        text: 'Wifi',
      },
      {
        icon: 'mdi-bluetooth',
        text: 'Bluetooth',
      },
      {
        icon: 'mdi-chart-donut',
        text: 'Data Usage',
      },
    ],
    model: 1,
    altColor: 'primary',
  }),
}
</script>