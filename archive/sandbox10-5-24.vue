<template>
  <v-row>
    <v-col cols="6">
      <h3>Jellyfin Session ID {{ session_id }}</h3>

      <v-card>
        <v-btn
          :class="[intervalID == '' ? 'mywarning' : 'myprimary']"
          @click="turnOnUpdating"
          >Turn on Jellyfin Monitor</v-btn
        >
        <v-btn @click="turnOffUpdating">Turn off Jellyfin Monitor</v-btn>
        <v-btn @click="">{{ isPaused }}</v-btn>
        <v-btn class="button" @click="getPlayStatus"
          ><v-icon>mdi-video</v-icon></v-btn
        >
        <div class="card-body">Request Status: {{ currentPosition }}</div>
      </v-card>
    </v-col>
    <v-col cols="6">
      <v-card>
        <h1>Send a message!</h1>
        <v-btn class="button" @click="sendMessage">Click Me!</v-btn>
        <h3>{{ messageSentStatus }}</h3>
      </v-card>
    </v-col>
  </v-row>
</template>
<script>
export default {
  data() {
    return {
      headers: {
        Authorization: "Mediabrowser Token=d035af26e54542e9a3a31785ec260e14",
        "Content-Type": "application/json",
      },
      currentPosition: "",
      isPaused: true,
      messageSentStatus: "",
      session_id: "",
      fetchedResponse: "",
      intervalID: "",
    };
  },
  methods: {
    sendMessage() {
      if (this.session_id == "") {
        console.log("session_id is empty");
        return;
      }
      const url =
        "http://192.168.0.202:8096/Sessions/" + this.session_id + "/Message";

      return fetch(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({
          Text: "Hellow From Vue!!!",
        }),
      }).then((response) => {
        console.log(response.status);
        if (response.status == 200) {
          this.messageSentStatus = response.statusText;
        } else {
          console.log("error: ", response);
          this.messageSentStatus = response.statusText;
        }
      });
    },
    myCallback(a, b) {
      // Your code here
      // Parameters are purely optional.
      console.log(a);
      console.log(b);
    },
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
              if (session.NowPlayingItem) {
                this.currentPosition = Math.floor(
                  session.PlayState.PositionTicks / 10_000_000
                );
                this.isPaused = session.PlayState.IsPaused;
              } else {
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
      this.intervalID = setInterval(
        this.getPlayStatus,
        1000,
        "Parameter 1",
        "Parameter 2"
      );
    },
    turnOffUpdating() {
      if (this.intervalID) clearInterval(this.intervalID);
      this.intervalID = "";
    },
  },
  created() {
    this.getPlayStatus();
  },
};
</script>
<style></style>
