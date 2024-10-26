<template>
  <div class="mt-4">
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <div class="mt-4">
          <v-badge color="error" offset-x="20" offset-y="10">
            <v-btn text v-bind="attrs" v-on="on">
              <v-img
                max-width="60px"
                max-height="60px"
                src="/static/public/icons/jellyfin.256x256.png"
              ></v-img>
            </v-btn>
          </v-badge>
        </div>
      </template>
      <v-card class="mx-auto" max-width="800" tile>
        <v-list shaped>
          <v-subheader>
            <span>
              <v-row justify="center">
                <h2>
                  <strong>{{ jellyfin_status.UserName }}</strong>
                </h2>
              </v-row>
              <v-row justify="center">
                <h2>server: atlas-HMTC</h2>
              </v-row>
            </span>
          </v-subheader>
          <v-list-item-group color="primary">
            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  >JF Session Id:
                  <strong> {{ jellyfin_status.Id }}</strong></v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>
                  <span
                    >Now Playing

                    {{ jellyfin_status.NowPlayingItem?.Name }}</span
                  ></v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>
                  jf_id
                  {{ jellyfin_status.NowPlayingItem?.Id }}</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  >RunTimeTicks{{
                    jellyfin_status.NowPlayingItem?.RunTimeTicks
                  }}</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  >PositionTicks{{
                    jellyfin_status.PlayState.PositionTicks
                  }}</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  >Jellyfin ID:{{ page_jellyfin_id }} (Page)</v-list-item-title
                >
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>HaveBothIDs</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <v-icon>mdi-pencil</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title>PageMatchesAudio </v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-list-item>
              <v-list-item-icon>
                <span v-if="jellyfin_status.PlayState.IsPaused">
                  <v-icon>mdi-play</v-icon>
                </span>
                <span v-else>
                  <v-icon>mdi-pause</v-icon>
                </span>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title><<<<<>>>>> </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-card>
    </v-menu>
  </div>
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
    if (this.jellyfin_status.NowPlayingItem) {
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
  },
};
</script>
<style></style>
