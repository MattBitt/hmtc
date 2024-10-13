<template>
  <v-container class="fill-height">
    <!-- The following cases are considered
  
        1. server not found - disable everything (ERROR)
        2. no eligible client sessions - disable everything (WARNING)
        3. found multiple client sessions - disable everything (??)
        4. 1 client session - not playing anything (Load in Jellyfin)
        5. 1 client session - playing something different than on the page (jellyfin id in hmtc db) what you see != what you hear 
        6. 1 client session - playing something different than on the page (jellyfin id NOT in hmtc db)
        7. 1 client session - playing whats on the page - play and pause -->

    <v-row justify="end" class="">
      <v-col cols="8">
        <v-row id="row1" justify="center">
          <span v-if="hasItemLoaded">
            <span class="medium-timer">{{ timeString }}</span>

            <v-btn class="button" @click="playpause_jellyfin()">
              <v-icon>{{ isPaused ? "mdi-play" : "mdi-pause" }}</v-icon>
            </v-btn>

            <v-btn class="button" @click="stop_jellyfin()">
              <v-icon>mdi-stop</v-icon>
            </v-btn>
          </span>

          <!-- <span
            v-else-if=""
            justify="center"
          > -->
          <span
            v-else-if="
              (JSON.stringify(this.jellyfin_status.session_id) != '{}') &
              this.jellyfin_status.is_connected
            "
          >
            <v-btn
              class="button"
              @click="open_video_in_jellyfin(this.jellfin_status?.jellyfin_id)"
              >Open in Jellyfin</v-btn
            >
          </span>
          <span v-else class="">
            <v-row justify="center">
              <h2>
                <strong>{{ jellyfin_status.user }}</strong>
              </h2>
            </v-row>
            <v-row justify="center">
              <h2>server: atlas-HMTC</h2>
            </v-row>
          </span>
        </v-row>
      </v-col>
      <v-col cols="4">
        <v-row justify="center" class="mr-8">
          <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-badge :color="jellyfinColor" offset-x="20" offset-y="10">
                <v-btn text v-bind="attrs" v-on="on">
                  <v-img
                    max-width="60px"
                    max-height="60px"
                    src="/static/public/icons/jellyfin.256x256.png"
                  ></v-img>
                </v-btn>
              </v-badge>
            </template>
            <v-list>
              <v-list-item
                >Is Connected:
                {{ this.jellyfin_status.is_connected }}</v-list-item
              >
              <v-list-item
                >Jellyfin ID:
                {{ this.jellyfin_status?.jellyfin_id }} (Client)</v-list-item
              >
              <v-list-item
                >Jellyfin ID:{{ page_jellyfin_id }} (Page)</v-list-item
              >
              <v-list-item>HaveBothIDs{{ HaveBothIDs }}</v-list-item>
              <v-list-item>PageMatchesAudio {{ PageMatchesAudio }}</v-list-item>
              <v-list-item
                >JF Session: {{ jellyfin_status.session_id }}</v-list-item
              >
              <v-list-item>is Paused {{ isPaused }}</v-list-item>
            </v-list>
          </v-menu>
        </v-row>
      </v-col>
    </v-row>
    <v-row id="row2">
      <v-row v-if="HaveBothIDs & !PageMatchesAudio & hasItemLoaded">
        <span class="mywarning"> What You See != What You Hear!</span>

        <v-btn text @click="loadPageForPlayingAudio()">Page</v-btn>

        <span>Change?</span>

        <v-btn text @click="open_video_in_jellyfin()">Audio</v-btn>
      </v-row>
    </v-row>
  </v-container>
</template>
<script>
module.exports = {
  name: "VideoDetailsJFBar",
  props: { jellyfin_status: Object, page_jellyfin_id: String, api_key: String },

  data() {
    return {
      hasItemLoaded: false,
      debugMode: false,
      // page_jellyfin_id: "",
      jellyfin_status: {},

      currentPosition: "",
      isPaused: true,
      liveUpdating: false,
      intervalID: "",
      fetchedResponse: "",
    };
  },
  methods: {
    loadPageForPlayingAudio() {
      // BROKEN
      // if (this.jellyfin_status.jellyfin_id != null) {
      //   this.open_detail_page(this.jellyfin_status.jellyfin_id);
      // }
    },
    getPlayStatus() {
      // if (this.jellyfin_status.session_id == "") {
      //   return;
      // }
      const fetchPromise = fetch(
        "http://192.168.0.202:8096/Sessions?ActiveWithinSeconds=300",
        {
          headers: this.headers,
        }
      );
      fetchPromise.then((response) => {
        if (response.status == 200) {
          response.json().then((data) => {
            const session = data.find(
              (item) => item.Id === this.jellyfin_status.session_id
            );
            if (session) {
              this.fetchedResponse = JSON.stringify(session);
              if (session.NowPlayingItem) {
                this.hasItemLoaded = true;
                // this.page_jellyfin_id = session.NowPlayingItem.Id;
                // shouldn't modify since its a prop, right?
                this.currentPosition = Math.floor(
                  session.PlayState.PositionTicks / 10_000_000
                );
                this.isPaused = session.PlayState.IsPaused;
              } else {
                this.hasItemLoaded = false;
              }
            }

            this.refresh_jellyfin_status();
          });
        } else {
          console.log("error: ", response);
          this.turnOffUpdating();
        }
      });
    },
    turnOnUpdating() {
      this.liveUpdating = true;
      this.intervalID = setInterval(
        this.getPlayStatus,
        3000,
        "Parameter 1",
        "Parameter 2"
      );
    },
    turnOffUpdating() {
      this.liveUpdating = false;
      if (this.intervalID) clearInterval(this.intervalID);
      this.intervalID = "";
    },
    toggleUpdating() {
      if (this.liveUpdating) {
        this.turnOffUpdating();
      } else {
        this.turnOnUpdating();
      }
    },
  },
  created() {
    if (this.jellyfin_status.is_connected) {
      this.getPlayStatus();
      this.turnOnUpdating();
    } else {
      console.log("Not connected. not updating...");
    }
  },
  computed: {
    headers() {
      return {
        "Content-Type": "application/json",
        Authorization: "Mediabrowser Token=" + this.api_key,
      };
    },
    timeString() {
      return new Date(this.currentPosition * 1000)
        .toISOString()
        .substring(11, 19);
    },
    PageMatchesAudio() {
      return this.jellyfin_status.jellyfin_id == this.page_jellyfin_id;
    },
    HaveBothIDs() {
      console.log(
        this.jellyfin_status.jellyfin_id,
        this.page_jellyfin_id,
        this.jellyfin_status.jellyfin_id != null && this.page_jellyfin_id != ""
      );
      return (
        this.jellyfin_status.jellyfin_id != null && this.page_jellyfin_id != ""
      );
    },
    jellyfinColor() {
      if (this.PageMatchesAudio & this.HaveBothIDs) {
        // item is loaded, and matches the page
        // enable all jellyfin controls on the page
        return "myprimary";
      } else if (this.hasItemLoaded) {
        // item is loaded, a user session was found, but not the same as the page
        return "mywarning";
      } else if (this.jellyfin_status.session_id != "") {
        // jellyfin is connected, a user session was found,
        // but no item is loaded
        return "mylight";
      } else if (this.jellyfin_status.is_connected) {
        // jellyfin is connected, but no user session was found
        return "mydark";
      } else {
        // jellyfin isn't connected
        return "myerror";
      }
    },
  },
};
</script>
<style>
.border1 {
  border: 1px solid black;
}
.border2 {
  border: 1px solid orange;
}
.border3 {
  border: 1px solid blue;
}
</style>
