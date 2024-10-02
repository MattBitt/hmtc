<template>
  <v-container>
    <v-row>
      <v-col cols="3">
        <v-sheet class="">
          <v-row class="pa-2" justify="center">
            <v-img
              :class="[isConnected ? '' : 'myerror']"
              src="/static/public/icons/jellyfin.1024x1023.png"
              max-width="60px"
            ></v-img>
          </v-row>
        </v-sheet>
        <v-sheet class="pa-2">
          <v-row class="" justify="center">
            <div v-if="isConnected">
              <v-btn
                :class="[liveUpdating ? 'myprimary' : 'mywarning']"
                @click="toggleUpdating"
                ><v-icon>mdi-cloud-download-outline</v-icon></v-btn
              >
            </div>
          </v-row>
        </v-sheet>
      </v-col>
      <v-col cols="9">
        <v-sheet class="pa-4">
          <v-row>
            <h3>{{ isConnected ? "Connected" : "Disconnected" }}</h3>
            <div v-if="isConnected">
              {{ hasItemLoaded ? "Item Loaded" : "Nothing Loaded" }}
              <div v-if="hasItemLoaded">
                {{ isPaused ? "Paused" : "Playing" }}
                <h3>Position: {{ currentPosition }}</h3>
              </div>
              <v-divider></v-divider>
            </div>
          </v-row>
          <v-row>
            <div v-if="debugMode">
              <h5>Video Jellyfin id</h5>

              <span>{{ jellyfin_id }}</span>
              <h5>Client Jellyfin id:</h5>
              <span>{{ loadedItemJellyfinId }}</span>
            </div>
          </v-row>
          <v-row>
            {{ jellyfin_id === loadedItemJellyfinId ? "Ready" : "Not Ready" }}
          </v-row>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      debugMode: true,
      isConnected: false,
      hasItemLoaded: false,
      loadedItemJellyfinId: "",
      currentPosition: "",
      isPaused: true,
      liveUpdating: false,
      session_id: "",
      jellyfin_id: "",
      api_key: "d035af26e54542e9a3a31785ec260e14",
      intervalID: "",
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
        console.log("session_id is empty");
        return;
      }
      const fetchPromise = fetch(
        "http://192.168.0.202:8096/Sessions?ActiveWithinSeconds=300",
        {
          headers: this.headers,
        }
      );
      fetchPromise.then((response) => {
        // this.fetchedResponse = response.statusText;
        if (response.status == 200) {
          response.json().then((data) => {
            const session = data.find((item) => item.Id === this.session_id);
            if (session) {
              this.isConnected = true;
              if (session.NowPlayingItem) {
                this.hasItemLoaded = true;
                this.loadedItemJellyfinId = session.NowPlayingItem.Id;
                this.currentPosition = Math.floor(
                  session.PlayState.PositionTicks / 10_000_000
                );
                this.isPaused = session.PlayState.IsPaused;
              } else {
                this.hasItemLoaded = false;
                // console.log("Nothing is playing");
              }
            } else {
              this.isConnected = false;
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
    this.turnOnUpdating();
  },
  computed: {
    headers() {
      return {
        "Content-Type": "application/json",
        Authorization: "Mediabrowser Token=" + this.api_key,
      };
    },
  },
};
</script>
<style></style>
