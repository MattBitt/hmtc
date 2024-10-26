<template>
  <div class="mt-4">
    <!-- <v-btn @click="turnOffUpdating" color="primary" dark>Turn Off Live</v-btn> -->
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <div class="mt-4">
          <v-badge :color="jellyfinBadgeColor" offset-x="20" offset-y="10">
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
            <v-row justify="center">
              <h2>
                <strong color="primary--text">{{
                  jellyfin_status.UserName
                }}</strong>
              </h2>
            </v-row>
            <v-row justify="center">
              <h2>server: atlas-HMTC</h2>
            </v-row>
          </v-subheader>
          <v-list-item-group>
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
                <v-list-item-title>HaveBothIDs</v-list-item-title>
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
                <v-list-item-title>
                  <v-row>
                    <v-col cols="4">
                      {{ currentPlayState.PositionTicks / 10000000 }}
                    </v-col>
                    <v-col cols="4">
                      {{ currentPlayState.IsPaused }}
                    </v-col>
                    <v-col cols="4"> </v-col>
                  </v-row>
                </v-list-item-title>
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
  props: {
    enable_live_updating: Boolean,
    jellyfin_status: Object,
    page_jellyfin_id: String,
  },

  data() {
    return {
      jellyfin_status: {},
      intervalID: "",
    };
  },
  methods: {
    updatePlayState() {
      // console.log("Updating...");
      this.update_play_state();
    },
    turnOnUpdating() {
      this.intervalID = setInterval(
        this.updatePlayState,
        5000,
        "Parameter 1",
        "Parameter 2"
      );
    },
    turnOffUpdating() {
      if (this.intervalID) {
        console.log("clearing interval");
        clearInterval(this.intervalID);
      }
      this.intervalID = "";
    },
  },
  created() {
    if (this.enable_live_updating) {
      console.log("Connected. updating...");
      this.turnOnUpdating();
    } else {
      console.log("Not connected. not updating...");
    }
  },
  computed: {
    currentPlayState() {
      return this.jellyfin_status.PlayState;
    },
    jellyfinBadgeColor() {
      if (!this.enable_live_updating) {
        return "error";
      } else if (this.jellyfin_status.Id != "") {
        return "primary";
      } else {
        return "warning";
      }
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
