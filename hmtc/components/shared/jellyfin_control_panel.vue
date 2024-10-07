<template>
  <div>
    <v-row justify="space-between" class="mx-4">
      <v-btn small class="button" @click="debugMode = !debugMode">
        <v-icon>mdi-spider</v-icon>
      </v-btn>
      <!-- <v-img src="/static/public/icons/jellyfin.1024x1023.png" contain> -->
      <v-switch v-model="liveUpdating" color="primary" label="Live"></v-switch>
    </v-row>
    <!-- The following cases are considered

      1. server not found - disable everything (ERROR)
      2. no eligible client sessions - disable everything (WARNING)
      3. found multiple client sessions - disable everything (??)
      4. 1 client session - not playing anything (Load in Jellyfin)
      5. 1 client session - playing something different than on the page (jellyfin id in hmtc db) what you see != what you hear 
      6. 1 client session - playing something different than on the page (jellyfin id NOT in hmtc db)
      7. 1 client session - playing whats on the page - play and pause -->

    <v-row v-if="!is_server_connected">
      <v-img
        src="/static/public/icons/x.png"
        max-height="20px"
        max-width="20px"
      ></v-img>
      <span class="ml-4">1. Python could find the server. Good Luck</span>
    </v-row>

    <v-row v-if="!has_active_session">
      <v-img
        src="/static/public/icons/x.png"
        max-height="20px"
        max-width="20px"
      ></v-img>
      <span class="ml-4">2. No Active Session</span>
    </v-row>

    <v-row justify="center" v-else>
      <v-row v-if="hasItemLoaded" class="">
        <p class="medium-timer mt-2">{{ timeString }}</p>
        <v-btn small class="button" @click="playpause_jellyfin()">
          <v-icon>{{ isPaused ? "mdi-play" : "mdi-pause" }}</v-icon>
        </v-btn>
        <v-btn small class="button" @click="stop_jellyfin()">
          <v-icon>mdi-stop</v-icon>
        </v-btn>

        <v-row justify="center">
          <v-col v-if="jellyfin_id == loadedItemJellyfinId">
            <v-row class="">
              <v-img
                src="/static/public/icons/check.png"
                max-height="20px"
                max-width="20px"
              ></v-img>
              <span class="ml-4">7. What You See == What You Hear!</span>
            </v-row>
          </v-col>
          <v-col v-else>
            <v-row
              v-if="(jellyfin_id != '') | (loadedItemJellyfinId != '')"
              class="mywarning"
            >
              <v-img
                src="/static/public/icons/x.png"
                max-height="20px"
                max-width="20px"
              ></v-img>
              <span class="ml-4">What You See != What You Hear</span>

              <v-row justify="center">
                <v-btn
                  class="button"
                  @click="open_detail_page(loadedItemJellyfinId)"
                  >Page</v-btn
                >

                <v-btn class="button" @click="open_video_in_jellyfin()"
                  >Audio</v-btn
                >
                <p>Which to Change</p>
              </v-row>
            </v-row>
            <v-row v-else>
              <span>I think shows up if the jellyfin id is not in the db?</span>
            </v-row>
          </v-col>
        </v-row>
      </v-row>
      <v-row justify="center" v-else>
        <p>4. Active Session Found but nothing is playing</p>
        <v-btn class="button" @click="open_video_in_jellyfin()"
          >Open in Jellyfin</v-btn
        >
      </v-row>
    </v-row>

    <div v-if="debugMode">
      <h3>Debug Mode</h3>
      <!-- <p>{{ fetchedResponse }}</p> -->
      {{ hasItemLoaded ? "" : "Nothing Playing" }}
      <h3>{{ is_connected ? "" : "Disconnected" }}</h3>
      <span>{{ jellyfin_id }}</span>
      <h5>Client Jellyfin id:</h5>
      {{ isPaused ? "Paused" : "Playing" }}
      <span>{{ loadedItemJellyfinId }}</span>
      <v-btn
        :class="[liveUpdating ? 'myprimary' : 'mywarning']"
        @click="toggleUpdating"
        ><v-icon>mdi-cloud-download-outline</v-icon></v-btn
      >
    </div>
  </div>
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
  },
};
</script>
<style></style>
