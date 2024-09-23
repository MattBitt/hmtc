<template>
  <!-- Main Data Table -->
  <v-data-table
    :headers="_headers"
    :items="items"
    sort-by.sync="sortBy"
    :sort-desc.sync="sortDesc"
    :search="search"
    :items-per-page="30"
    class="elevation-1"
    :single-expand="true"
    expanded.sync="expanded"
    item-key="title"
    @pagination="writeLog"
    @click:row="handleClick"
    show-expand
  >
    <template v-slot:top="{ pagination, options, updateOptions }">
      <v-toolbar flat>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
        <v-divider inset vertical></v-divider>
        <v-data-footer
          :pagination="pagination"
          :options="options"
          @update:options="updateOptions"
          items-per-page-text="$vuetify.dataTable.itemsPerPageText"
        />
        <v-spacer></v-spacer>
        <!-- New/Edit Modal Dialog Starts Here -->
        <v-dialog v-model="dialog" max-width="800px">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="button mb-2" v-bind="attrs" v-on="on">
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
                      v-model="editedItem.jellyfin_id"
                      label="Jellyfin ID"
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
                  <v-col cols="12" sm="6" md="4">
                    <v-select
                      v-model="selected_album"
                      :items="albums"
                      item-text="title"
                      item-value="id"
                      label="Album"
                      return-object
                    ></v-select
                  ></v-col>
                </v-row>
              </v-container>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn class="button" @click="close"> Cancel </v-btn>
              <v-btn class="button" text @click="saveItemToDB(editedItem)">
                Save
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <!-- Delete Dialog -->
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title class="text-h5"
              >Are you sure you want to delete this item?</v-card-title
            >
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn class="button" @click="closeDelete">Cancel</v-btn>
              <v-btn class="button" @click="deleteItemConfirm">OK</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-toolbar>
    </template>
    <!-- Custom cell contents for each column-->
    <template v-slot:item.contains_unique_content="{ item }">
      <v-simple-checkbox
        v-model="item.contains_unique_content"
      ></v-simple-checkbox>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-icon x-large class="mylight ml-1 mr-4" @click="editItem(item)">
        mdi-pencil
      </v-icon>
      <v-icon x-large class="mylight mr-1" @click="link1_clicked(item)">
        mdi-rhombus-split
      </v-icon>
    </template>
    <template v-slot:no-data>
      <v-btn class="button" @click=""> Reset </v-btn>
    </template>
    <template v-slot:expanded-item="{ headers, item }">
      <td :colspan="headers.length">
        <v-chip>
          <span v-if="item.channel_name">
            <a
              :href="
                '/videos/channel/' +
                channels.find((channel) => channel.name === item.channel_name)
                  .id
              "
            >
              {{ item.channel_name }}
            </a>
          </span>
          <span v-else>---</span>
        </v-chip>
        <v-chip>
          <span v-if="item.youtube_series_title">
            <a
              :href="
                '/videos/series/' +
                youtube_serieses.find(
                  (youtube_series) =>
                    youtube_series.title === item.youtube_series_title
                ).id
              "
            >
              {{ item.youtube_series_title }}
            </a>
          </span>
          <span v-else>---</span>
        </v-chip>
        <v-chip>
          <span v-if="item.album_title">
            <a
              :href="
                '/videos/album/' +
                albums.find((album) => album.title === item.album_title).id
              "
            >
              {{ item.album_title }}
            </a>
          </span>
          <span v-else>---</span>
        </v-chip>
        <v-chip>
          <span v-if="item.series_name">
            <a
              :href="
                '/videos/series/' +
                serieses.find((series) => series.name === item.series_name).id
              "
            >
              {{ item.series_name }}
            </a>
          </span>
          <span v-else>---</span>
        </v-chip>
        <v-chip :class="getColor(item)">
          {{ item.duration }}
        </v-chip>
      </td>
    </template>
  </v-data-table>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      dialogDelete: false,
      sortBy: "title",
      sortDesc: true,
      search: "",
      headers: [
        // { text: "id", value: "id", filterable: true },
        {
          text: "Uploaded",
          value: "upload_date",
          filterable: false,
          width: "20%",
          align: "start",
        },

        {
          text: "Title",
          value: "title",
          align: "start",
        },
        // { text: "Duration (s)", value: "duration", filterable: false },
        // { text: "Series Name", value: "series_name", filterable: true },
        // {
        //   text: "Youtube Series",
        //   value: "youtube_series_title",
        //   filterable: true,
        // },
        // { text: "Episode", value: "episode", filterable: true },
        // { text: "Jellyfin ID", value: "jellyfin_id", filterable: true },
        // { text: "Album Title", value: "album_title", filterable: true },

        // { text: "Channel Name", value: "channel_name", filterable: false },
        // {
        //   text: "Playlist Title",
        //   value: "playlist_title",
        //   filterable: false,
        // },
        { text: "Unique", value: "contains_unique_content", filterable: false },
        {
          text: "",
          value: "actions",
          sortable: false,
          filterable: false,
          width: "30%",
          align: "end",
        },
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

      albums: [
        {
          id: 1,
          title: "youtube_playlist 1",
        },
      ],

      selected_album: {
        id: 1,
        title: "youtube_playlist 1",
      },

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
          jellyfin_id: "",
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
        jellyfin_id: "",
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
        jellyfin_id: "",
      },
      expanded: [],
    };
  },

  computed: {
    formTitle() {
      return this.editedIndex === -1 ? "New Item" : "Edit Item";
    },

    _headers() {
      let h = this.headers;

      if (!this.show_nonunique) {
        h = h.filter((x) => x.value !== "contains_unique_content");
      }
      return h.filter((x) => !x.value.includes(this.hide_column));
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
    getColor(item) {
      if (item.duration < 60) return "mydark";
      else if (item.duration < 900) return "mylight";
      else return "myprimary";
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

      this.editedItem.album = this.albums.find(
        (album) => album.title === item.album_title
      );

      this.selected_channel = this.editedItem.channel || this.selected_channel;

      this.selected_series = this.editedItem.series || this.selected_series;

      this.selected_youtube_series =
        this.editedItem.youtube_series || this.selected_youtube_series;

      this.selected_playlist =
        this.editedItem.playlist || this.selected_playlist;

      this.selected_album = this.editedItem.album || this.selected_album;

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
        selectedAlbum: this.selected_album,
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
    writeLog(paginationObject) {
      // this is an example of intercepting the pagination event
      // to perform some action
      let action;
      console.log(paginationObject);
      this.currentPage < paginationObject.page
        ? (action = "forward")
        : (action = "backguard");
      this.currentPage = paginationObject.page;
      console.log(action);
      //Write code to call your backend using action...
    },
    // this function captures events for the data table
    handleClick(row) {
      // this.items.map((item, index) => {
      //   item.selected = item === row;
      //   this.$set(this.items, index, item);
      // });
      // console.log(row);
    },
  },
};
</script>
<style></style>
