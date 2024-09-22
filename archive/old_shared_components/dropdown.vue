<template>
  <div class="text-center">
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn :color="color" dark v-bind="attrs" v-on="on">
          {{ caption }}
        </v-btn>
      </template>

      <!-- <v-list>
        <v-list-item v-for="(item, index) in items" :key="index">
          <v-list-item-title
            ><v-btn :color="color" dark @click="on_click(item)">{{
              item.title
            }}</v-btn></v-list-item-title
          >
        </v-list-item>
      </v-list> -->
    </v-menu>
  </div>
</template>
<script>
export default {
  data: () => ({
    caption: "Click Me!",
    color: "pink",
    items: [
      { title: "Click Me 1 " },
      { title: "Click Me 2" },
      { title: "Click Me 3" },
      { title: "Click Me 2" },
    ],
  }),
};
</script>
