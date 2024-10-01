<template>
  <v-container>
    <v-row>
      <v-col cols="3">
        <v-img
          src="/static/public/icons/jellyfin.1024x1023.png"
          max-width="90px"
        ></v-img>
      </v-col>
      <v-col cols="6">
        <h3>isConnected {{ isConnected }}</h3>
        <h3>hasItemLoaded {{ hasItemLoaded }}</h3>
        <h3>currentPosition {{ currentPosition }}</h3>

        <span
          >Paused:
          <h3>{{ isPaused }}</h3></span
        >
      </v-col>
      <v-col cols="3">
        <v-btn
          :class="[liveUpdating ? 'myprimary' : 'mywarning']"
          @click="toggleUpdating"
          ><v-icon>mdi-cloud-download-outline</v-icon></v-btn
        >
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
export default {
  data() {
    return {
      headers: {
        Authorization: "Mediabrowser Token=d035af26e54542e9a3a31785ec260e14",
        "Content-Type": "application/json",
      },
      isConnected: false,
      hasItemLoaded: false,
      currentPosition: "",
      isPaused: true,
      liveUpdating: false,
      messageSentStatus: "",
      session_id: "",
      fetchedResponse: "",
      intervalID: "",
    };
  },
  methods: {
    // sendMessage() {
    //   if (this.session_id == "") {
    //     console.log("session_id is empty");
    //     return;
    //   }
    //   const url =
    //     "http://192.168.0.202:8096/Sessions/" + this.session_id + "/Message";

    //   return fetch(url, {
    //     method: "POST",
    //     headers: this.headers,
    //     body: JSON.stringify({
    //       Text: "Hellow From Vue!!!",
    //     }),
    //   }).then((response) => {
    //     this.isConnected = true;
    //     console.log(response.status);
    //     if (response.status == 200) {
    //       this.messageSentStatus = response.statusText;
    //     } else {
    //       console.log("error: ", response);
    //       this.messageSentStatus = response.statusText;
    //     }
    //   });
    // },

    getPlayStatus() {
      // GET request using fetch with set headers
      if (this.session_id == "") {
        console.log("session_id is empty");
        return;
      }
      return fetch(
        "http://192.168.0.202:8096/Sessions?ActiveWithinSeconds=300",
        {
          headers: this.headers,
        }
      ).then((response) => {
        this.fetchedResponse = response.statusText;
        if (response.status == 200) {
          response.json().then((data) => {
            const session = data.find((item) => item.Id === this.session_id);
            if (session) {
              this.isConnected = true;
              if (session.NowPlayingItem) {
                this.hasItemLoaded = true;
                this.currentPosition = Math.floor(
                  session.PlayState.PositionTicks / 10_000_000
                );
                this.isPaused = session.PlayState.IsPaused;
              } else {
                this.hasItemLoaded = false;
                console.log("Nothing is playing");
              }
            } else {
              console.log("Session not found");
            }
          });
        } else {
          console.log("error: ", response);
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
};
</script>
<style></style>
