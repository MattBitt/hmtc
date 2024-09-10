<template>
  <v-card>
    <v-card-title>
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
      ></v-text-field>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="items"
      sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      :search="search"
      :items-per-page="30"
      class="elevation-1"
      :single-expand="true"
      expanded.sync="expanded"
      item-key="title"
      show-expand
    >
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
                      <v-text-field
                        v-model="editedItem.title"
                        label="Title"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.duration"
                        label="Duration"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.episode"
                        label="Episode Number"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.youtube_id"
                        label="Youtube ID"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.upload_date"
                        label="Upload Date"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-checkbox
                        v-model="editedItem.contains_unique_content"
                        label="Unique Content"
                      ></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-select
                        v-model="selected_channel"
                        :items="channels"
                        item-text="name"
                        item-value="id"
                        label="Channel"
                        return-object
                      ></v-select
                    ></v-col>

                    <v-col cols="12" sm="6" md="4">
                      <v-select
                        v-model="selected_series"
                        :items="serieses"
                        item-text="name"
                        item-value="id"
                        label="Series"
                        return-object
                      ></v-select
                    ></v-col>

                    <v-col cols="12" sm="6" md="4">
                      <v-select
                        v-model="selected_youtube_series"
                        :items="youtube_serieses"
                        item-text="title"
                        item-value="id"
                        label="YouTube Series"
                        return-object
                      ></v-select
                    ></v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-select
                        v-model="selected_playlist"
                        :items="playlists"
                        item-text="title"
                        item-value="id"
                        label="YouTube Playlist"
                        return-object
                      ></v-select
                    ></v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="close">
                  Cancel
                </v-btn>
                <v-btn
                  color="blue darken-1"
                  text
                  @click="saveItemToDB(editedItem)"
                >
                  Save
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dialogDelete" max-width="500px">
            <v-card>
              <v-card-title class="text-h5"
                >Are you sure you want to delete this item?</v-card-title
              >
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeDelete"
                  >Cancel</v-btn
                >
                <v-btn color="blue darken-1" text @click="deleteItemConfirm"
                  >OK</v-btn
                >
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
        <v-simple-checkbox
          color="orange"
          v-model="item.contains_unique_content"
          disabled
        ></v-simple-checkbox>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon medium class="mr-2" @click="link_clicked(item)">
          mdi-rhombus-split
        </v-icon>
        <v-icon medium class="mr-2" @click="editItem(item)">
          mdi-pencil
        </v-icon>
        <v-icon medium color="red" @click="deleteItem(item)">
          mdi-delete
        </v-icon>
      </template>
      <template v-slot:no-data>
        <v-btn color="primary" @click=""> Reset </v-btn>
      </template>
      <template v-slot:expanded-item="{ headers, item }">
        <td :colspan="headers.length">
          Series: {{ item.series_name }} <br />
          Youtube Series: {{ item.youtube_series_title }}<br />
          Channel Name: {{ item.channel_name }}<br />
          Playlist Title: {{ item.playlist_title }}<br />
          Unique: {{ item.contains_unique_content }}<br />
        </td>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    dialog: false,
    dialogDelete: false,
    sortBy: "upload_date",
    sortDesc: true,
    search: "",
    headers: [
      { text: "Upload Date", value: "upload_date", filterable: false },

      {
        text: "Title",
        value: "title",
        align: "start",
        width: "20%",
      },
      { text: "Duration (s)", value: "duration", filterable: false },
      { text: "Series Name", value: "series_name", filterable: true },
      {
        text: "Youtube Series",
        value: "youtube_series_title",
        filterable: true,
      },
      { text: "Episode", value: "episode", filterable: true },
      { text: "Channel Name", value: "channel_name", filterable: false },
      {
        text: "Playlist Title",
        value: "playlist_title",
        filterable: false,
      },
      // { text: 'Unique', value: 'contains_unique_content', filterable: false },
      { text: "Actions", value: "actions", sortable: false },
    ],

    selected_channel: {
      id: 1,
      name: "Channel 1",
    },
    channels: [
      {
        id: 1,
        name: "Channel 1",
      },
    ],

    selected_series: {
      id: 1,
      name: "series 1",
    },
    serieses: [
      {
        id: 1,
        name: "series 1",
      },
    ],

    selected_youtube_series: {
      id: 1,
      title: "youtube_series 1",
    },

    youtube_serieses: [
      {
        id: 1,
        title: "youtube_series 1",
      },
    ],

    selected_playlist: {
      id: 1,
      title: "youtube_playlist 1",
    },

    playlists: [
      {
        id: 1,
        title: "youtube_playlist 1",
      },
    ],

    items: [
      {
        title: "Title 1",
        youtube_series_title: "Frozen Yogurt",
        episode: "",
        duration: 0,
        series: "",
        playlist: "",
        youtube_series: "",
        channel: "",
        series_name: "",
        playlist_title: "",
        channel_name: "",
        contains_unique_content: true,
        upload_date: "2021-01-01",
        id: 1,
      },
    ],

    editedIndex: -1,
    editedItem: {
      title: "Video Title",
      episode: "",
      duration: 0,
      series: "",
      playlist: "",
      youtube_series: "",
      channel: "",
      series_name: "",
      playlist_title: "",
      youtube_series_title: "",
      channel_name: "",
      contains_unique_content: true,
      upload_date: "",
      youtube_id: "",
      id: 0,
    },
    defaultItem: {
      title: "",
      episode: "",
      duration: 0,
      series: "",
      playlist: "",
      youtube_series: "",
      channel: "",
      series_name: "",
      playlist_title: "",
      youtube_series_title: "",
      channel_name: "",
      contains_unique_content: false,
      upload_date: "",
      youtube_id: "",
      id: 0,
    },
  }),

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Item" : "Edit Item";
    },
  },

  watch: {
    dialog(val) {
      val || this.close();
    },
    dialogDelete(val) {
      val || this.closeDelete();
    },
  },

  methods: {
    toggleOrder() {
      this.sortDesc = !this.sortDesc;
    },
    nextSort() {
      let index = this.headers.findIndex((h) => h.value === this.sortBy);
      index = (index + 1) % this.headers.length;
      this.sortBy = this.headers[index].value;
    },
    getColor(duration) {
      if (duration < 60) return "red";
      else if (duration < 900) return "orange";
      else return "green";
    },
    editItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);

      this.editedItem.channel = this.channels.find(
        (channel) => channel.name === item.channel_name
      );

      this.editedItem.series = this.serieses.find(
        (series) => series.name === item.series_name
      );

      this.editedItem.youtube_series = this.youtube_serieses.find(
        (youtube_series) => youtube_series.title === item.youtube_series_title
      );

      this.editedItem.playlist = this.playlists.find(
        (playlist) => playlist.title === item.playlist_title
      );

      this.selected_channel = this.editedItem.channel || this.selected_channel;

      this.selected_series = this.editedItem.series || this.selected_series;

      this.selected_youtube_series =
        this.editedItem.youtube_series || this.selected_youtube_series;

      this.selected_playlist =
        this.editedItem.playlist || this.selected_playlist;

      this.dialog = true;
    },

    deleteItem(item) {
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogDelete = true;
    },

    deleteItemConfirm() {
      this.items.splice(this.editedIndex, 1);
      this.delete_video_item(this.editedItem);
      this.closeDelete();
    },

    saveItemToDB(item) {
      // the function below is 'run' from python
      // actually saves the item in the db
      this.save_video_item({
        item: item,
        editedItem: this.editedItem,
        selectedChannel: this.selected_channel,
        selectedSeries: this.selected_series,
        selectedYoutubeSeries: this.selected_youtube_series,
        selectedPlaylist: this.selected_playlist,
      });

      // update the array in the front end and close the dialog box
      this.save();
      this.close();
    },

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    closeDelete() {
      this.dialogDelete = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    save() {
      if (this.editedIndex > -1) {
        Object.assign(this.items[this.editedIndex], this.editedItem);
      } else {
        this.items.push(this.editedItem);
      }
      this.close();
    },
  },
};
</script>
<style>
/* removes the items per page selector (doesn't work to display none)*/
.v-application--is-ltr .v-data-footer__pagination {
  margin-left: auto;
}
</style>
