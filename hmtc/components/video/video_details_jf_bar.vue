<template>
  <v-container class="">
    <!-- The following cases are considered
  
        1. server not found - disable everything (ERROR)
        2. no eligible client sessions - disable everything (WARNING)
        3. found multiple client sessions - disable everything (??)
        4. 1 client session - not playing anything (Load in Jellyfin)
        5. 1 client session - playing something different than on the page (jellyfin id in hmtc db) what you see != what you hear 
        6. 1 client session - playing something different than on the page (jellyfin id NOT in hmtc db)
        7. 1 client session - playing whats on the page - play and pause -->
    <v-toolbar flat>
      <v-row justify="end">
        <v-col cols="2">
          <!-- <span class="ml-4">1. Python could NOT find the server. Good Luck</span>
      </v-col>
      <v-col cols="4" v-else-if="!has_active_session">
        <span class="ml-4">Open a Client and Refresh the Page</span>
      </v-col>
      <v-col cols="4" v-else class="border3"> -->
          <v-badge :color="jellyfinColor" inline>
            <span>
              <v-img
                max-width="40px"
                max-height="40px"
                src="/static/public/icons/jellyfin.256x256.png"
              ></v-img>
            </span>
          </v-badge>
        </v-col>
        <v-col cols="10">
          <v-row>
            <span v-if="hasItemLoaded">
              <span class="medium-timer mb-2">{{ timeString }}</span>

              <v-btn class="button" @click="playpause_jellyfin()">
                <v-icon>{{ isPaused ? "mdi-play" : "mdi-pause" }}</v-icon>
              </v-btn>

              <v-btn class="button" @click="stop_jellyfin()">
                <v-icon>mdi-stop</v-icon>
              </v-btn>
            </span>
            <span v-if="PageMatchesAudio" cols="12" class="border1">
              <!-- Success Message would be here -->
            </span>
            <span v-else-if="HaveBothIDs & !PageMatchesAudio">
              <span class="mywarning"> What You See != What You Hear!</span>

              <v-btn
                class="button"
                @click="open_detail_page(loadedItemJellyfinId)"
                >Page</v-btn
              >

              <span>Change?</span>

              <v-btn class="button" @click="open_video_in_jellyfin()"
                >Audio</v-btn
              >
            </span>

            <span v-else justify="center">
              <v-btn class="button" @click="open_detail_page(jellyfin_id)"
                >Open in Jellyfin</v-btn
              >
            </span>

            <v-switch
              v-model="liveUpdating"
              color="primary"
              label=""
            ></v-switch>

            <v-menu offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn color="primary" dark v-bind="attrs" v-on="on">
                  <v-icon>mdi-spider</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item>Page Jellyfin ID</v-list-item>
                <v-list-item>{{ jellyfin_id }}</v-list-item>
                <v-list-item>Client Jellyfin id:</v-list-item>
                <v-list-item>{{ loadedItemJellyfinId }}</v-list-item>
              </v-list>
            </v-menu>
          </v-row>
        </v-col>
      </v-row>
    </v-toolbar>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      has_active_session: false,
      is_server_connected: false,
      can_seek: false,
      logoBackground: "",
      debugMode: false,
      is_connected: false,
      hasItemLoaded: false,
      loadedItemJellyfinId: "",
      currentPosition: "",
      isPaused: true,
      liveUpdating: false,
      session_id: "",
      jellyfin_id: "",
      api_key: "",
      intervalID: "",
      fetchedResponse: "",
    };
  },
  methods: {
    demo() {
      console.log("Function called!!");
      //return Promise.resolve("Success");
      // or
      return Promise.reject("Failure");
    },
    example() {
      this.demo().then(
        (message) => {
          console.log("Then success:" + message);
        },
        (message) => {
          console.log("Then failure:" + message);
        }
      );
    },
    getPlayStatus() {
      // GET request using fetch with set headers
      if (this.session_id == "") {
        // console.log("session_id is empty");
        this.logoBackground = "";
        return;
      }
      const fetchPromise = fetch(
        "http://192.168.0.202:8096/Sessions?ActiveWithinSeconds=300",
        {
          headers: this.headers,
        }
      );
      fetchPromise.then((response) => {
        if (response.status == 200) {
          response.json().then((data) => {
            const session = data.find((item) => item.Id === this.session_id);
            if (session) {
              this.fetchedResponse = JSON.stringify(session);
              this.is_connected = true;
              this.logoBackground = "mylight";
              if (session.NowPlayingItem) {
                this.hasItemLoaded = true;
                this.logoBackground = "";
                this.loadedItemJellyfinId = session.NowPlayingItem.Id;
                this.currentPosition = Math.floor(
                  session.PlayState.PositionTicks / 10_000_000
                );
                this.isPaused = session.PlayState.IsPaused;
              } else {
                this.hasItemLoaded = false;
                this.logoBackground = "myprimary";
                // console.log("Nothing is playing");
              }
            } else {
              this.is_connected = false;
              this.logoBackground = "mywarning";
              this.turnOffUpdating();
            }
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
        1000,
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
    console.log("Jellyfin Control Panel created");
    if (this.is_server_connected) {
      console.log("is_server was connected is true");
      this.is_connected = true;
      this.getPlayStatus();
      this.turnOnUpdating();
    } else {
      this.logoBackground = "myerror";
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
      return this.jellyfin_id == this.loadedItemJellyfinId;
    },
    HaveBothIDs() {
      return this.jellyfin_id != "" && this.loadedItemJellyfinId != "";
    },
    jellyfinColor() {
      if (this.PageMatchesAudio & this.HaveBothIDs) {
        return "primary";
      }
      if (this.hasItemLoaded) {
        return "success";
      }
      return this.is_connected ? "warning" : "error";
    },
  },
};
</script>
<style>
.border1 {
  border: 0px solid black;
}
.border2 {
  border: 1px solid orange;
}
.border3 {
  border: 0px solid blue;
}
</style>
