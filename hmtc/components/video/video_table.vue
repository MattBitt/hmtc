<template>
  <v-card>
    <v-card-title>
      <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line hide-details></v-text-field>
    </v-card-title>
    <v-data-table :headers="headers" :items="items" :sort-by.sync="sortBy" :sort-desc.sync="sortDesc" :search="search"
      items-per-page="30" class="elevation-1">
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Videos</v-toolbar-title>
          <v-divider class="mx-4" inset vertical></v-divider>
          <v-spacer></v-spacer>
          <v-dialog v-model="dialog" max-width="800px">
            <template v-slot:activator="{ on, attrs }">
              <v-btn color="primary" dark class="mb-2" v-bind="attrs" v-on="on">
                New Item
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5">{{ formTitle }}</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.title" label="Title"></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.duration" label="Duration"></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.series_name" label="Series Name"></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.youtube_series_title" label="Youtube Series"></v-text-field>
                    </v-col>

                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.channel_name" label="Channel Name"></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field v-model="editedItem.playlist_title" label="Playlist Title"></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-checkbox v-model="editedItem.contains_unique_content"
                        label="Contains Unique Content"></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-select v-model="selected_channel" :hint="`${selected_channel.name}`" :items="channels"
                        item-text="name" item-value="id" label="Channel" return-object single-line></v-select></v-col>

                    <v-col cols="12" sm="6" md="4">
                      <v-select v-model="selected_series" :hint="`${selected_series.name}, ${selected_series.id}`"
                        :items="serieses" item-text="name" item-value="id" label="Series" return-object
                        single-line></v-select></v-col>

                    <v-col cols="12" sm="6" md="4">
                      <v-select v-model="selected_youtube_series"
                        :hint="`${selected_youtube_series.title}, ${selected_youtube_series.id}`"
                        :items="youtube_serieses" item-text="title" item-value="id" label="YouTube Series" return-object
                        single-line></v-select></v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="close">
                  Cancel
                </v-btn>
                <v-btn color="blue darken-1" text @click="saveItem(editedItem)">
                  Save
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dialogDelete" max-width="500px">
            <v-card>
              <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
                <v-btn color="blue darken-1" text @click="deleteItemConfirm">OK</v-btn>
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
      </template>
      <template v-slot:item.duration="{ item }">
        <v-chip :color="getColor(item.duration)" dark>
          {{ item.duration }}
        </v-chip>
      </template>
      <template v-slot:item.contains_unique_content="{ item }">
        <v-simple-checkbox v-model="item.contains_unique_content" disabled></v-simple-checkbox>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon small class="mr-2" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon small @click="deleteItem(item)">
          mdi-delete
        </v-icon>
      </template>
      <template v-slot:bottom> </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click="">
          Reset
        </v-btn>
      </template>
    </v-data-table>
    <div class="text-center pt-2">

      <v-btn color="primary" class="mr-2" @click="toggleOrder">
        Toggle sort order
      </v-btn>
      <v-btn color="primary" @click="nextSort">
        Sort next column
      </v-btn>
    </div>
  </v-card>


</template>

<script>
export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    sortBy: 'upload_date',
    sortDesc: true,
    search: '',
    headers: [
      { text: 'Upload Date', value: 'upload_date', filterable: false },

      {
        text: 'Title',
        align: 'start',
        value: 'title',
        width: '20%',
      },
      { text: 'Duration (s)', value: 'duration', filterable: false },
      { text: 'Series Name', value: 'series_name', filterable: false },
      { text: 'Youtube Series', value: 'youtube_series_title', filterable: false },
      { text: 'Episode', value: 'episode', filterable: false, },
      // { text: 'Channel Name', value: 'channel_name', filterable: false },
      // { text: 'Playlist Title', value: 'playlist_title', filterable: false, width: '10%', },
      // { text: 'Unique', value: 'contains_unique_content', filterable: false },
      { text: 'Actions', value: 'actions', sortable: false },
    ],

    selected_channel: {
      name: 'Channel 1',
      id: 1,
    },
    channels: [
      {
        id: 1,
        name: 'Channel 1',
      },
      {
        id: 2,
        name: 'Channel 2',
      },
      {
        id: 3,
        name: 'Channel 3',
      },
    ],

    selected_series: {
      name: 'series 1',
      id: 1,
    },
    serieses: [
      {
        id: 1,
        name: 'series 1',
      },
      {
        id: 2,
        name: 'series 2',
      },
      {
        id: 3,
        name: 'series 3',
      },
    ],

    selected_youtube_series: {
      title: 'youtube_series 1',
      id: 1,
    },
    youtube_serieses: [
      {
        id: 1,
        title: 'youtube_series 1',
      },
      {
        id: 2,
        title: 'youtube_series 2',
      },
      {
        id: 3,
        title: 'youtube_series 3',
      },
    ],


    items: [
      {
        title: 'Title 1',
        youtube_series_title: 'Frozen Yogurt',
        episode: 159,
        duration: 6.0,
        series_name: "omegle",
        playlist_title: 4.0,
        channel_name: 1,
        contains_unique_content: true,
        upload_date: '2021-01-01',
        id: 1,
      },
      {
        title: 'Title 2',
        youtube_series_title: 'Ice cream sandwich',
        episode: 237,
        duration: 9.0,
        series_name: "omegle",
        playlist_title: 4.3,

        youtube_series_title: 'qwerty',
        channel_name: 1,
        contains_unique_content: true,
        id: 2,
      },
      {
        title: 'Title 3',
        youtube_series_title: 'Eclair',
        episode: 262,
        duration: 16.0,
        series_name: "guerrilla",
        playlist_title: 6.0,
        channel_name: 7,
        contains_unique_content: false,
        id: 3,
      },

    ],

    editedIndex: -1,
    editedItem: {
      title: 'Title 2',
      episode: 237,
      duration: 9.0,
      series_name: 37,
      playlist_title: 4.3,
      youtube_series_title: 'asdf',
      channel_name: 1,
      contains_unique_content: true,
      id: 2,
    },
    defaultItem: {
      title: 'Title 99',
      episode: 237,
      duration: 9.0,
      series_name: "omegle",
      playlist_title: 4.3,
      youtube_series_title: 'asdf',
      channel_name: 1,
      contains_unique_content: true,
      id: 15,
    },





  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item'
    },
  },

  watch: {
    dialog(val) {
      val || this.close()
    },
    dialogDelete(val) {
      val || this.closeDelete()
    },
  },



  methods: {
    toggleOrder() {
      this.sortDesc = !this.sortDesc
    },
    nextSort() {
      let index = this.headers.findIndex(h => h.value === this.sortBy)
      index = (index + 1) % this.headers.length
      this.sortBy = this.headers[index].value
    },
    getColor(duration) {
      if (duration < 60) return 'red'
      else if (duration < 900) return 'orange'
      else return 'green'
    },
    editItem(item) {
      console.log("Edit Item arg passed: ", item)
      this.editedIndex = this.items.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.editedItem.channel = this.channels.find((channel) => channel.name === item.channel_name)
      this.editedItem.series = this.serieses.find((series) => series.name === item.series_name)
      console.log(this.youtube_serieses)
      this.editedItem.youtube_series = this.youtube_serieses.find((youtube_series) => youtube_series.title === item.youtube_series)
      console.log("Edited Item after additions: ", this.editedItem)
      this.dialog = true

    },

    deleteItem(item) {
      this.editedIndex = this.items.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialogDelete = true
    },

    deleteItemConfirm() {
      this.items.splice(this.editedIndex, 1)
      this.closeDelete()
    },

    saveItem(item) {
      // function called from python

      this.save_video_item({
        item: item, editedItem: this.editedItem,
        selectedChannel: this.selected_channel,
        selectedSeries: this.selected_series,
        selectedYoutubeSeries: this.selected_youtube_series
      })
      this.close()
    },

    close() {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    closeDelete() {
      this.dialogDelete = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.items[this.editedIndex], this.editedItem)
      } else {
        this.items.push(this.editedItem)
      }
      this.close()
    },
  },
}

</script>
<style>
/* removes the items per page selector */
.v-application--is-ltr .v-data-footer__pagination {
  margin-left: auto;

}
</style>