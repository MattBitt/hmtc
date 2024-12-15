<template>
  <div>
    <v-sheet light v-if="this.sectionItems.length > 0"> </v-sheet>
    <v-expansion-panels focusable popout>
      <v-expansion-panel
        v-for="(section, index) in sectionItems"
        :key="section.id"
        v-model="slides"
      >
        <v-expansion-panel-header>
          <v-container>
            <v-range-slider
              :value="[section.start / 1000, section.end / 1000]"
              :max="video_duration"
              min="0"
              show-ticks="always"
              tick-size="4"
              readonly
              color="primary"
            >
              <template v-slot:prepend>
                <span class="tracknumber">{{ (index + 1).toString() }}</span>
              </template>
            </v-range-slider>
            <v-row justify="center">
              <v-col cols="2">
                <h4 class="primary--text font-weight-bold">
                  {{ durationString((section.end - section.start) / 1000) }}
                </h4>
              </v-col>
              <v-col cols="8">
                <h4 class="primary--text font-weight-bold">
                  {{ section.topics?.map(({ text }) => text).join(", ") }}
                </h4>
              </v-col>
            </v-row>
          </v-container>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-row class="">
            <v-col cols="6">
              <SummaryPanel
                :section="section"
                :topics="section.topics"
              ></SummaryPanel>
            </v-col>
            <!-- <v-col cols="6">
              <div v-if="section.track.title == 'No Track'">
                <SectionTrackForm
                  :section="section"
                  @saveTrack="createTrack2"
                  :defaultTrackTitle="computedDefaultTrackTitle"
                />
              </div>
              <div v-else>
                <SectionTrackPanel
                  :section="section"
                  :track="section.track"
                  @removeTrack="removeTrack"
                  @createAudioFile="createAudioFile"
                  @deleteAudioFile="deleteAudioFile"
                  @createLyricsFile="createLyricsFile"
                  @deleteLyricsFile="deleteLyricsFile"
                />
              </div>
            </v-col> -->
            <v-spacer></v-spacer>
          </v-row>

          <v-row justify="center" class="mt-10">
            <v-dialog
              v-model="dialog[index]"
              fullscreen
              hide-overlay
              transition="dialog-bottom-transition"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn color="primary" dark v-bind="attrs" v-on="on">
                  <v-icon>mdi-pencil</v-icon>Edit Section
                </v-btn>
              </template>

              <v-toolbar dark color="primary">
                <v-btn icon dark @click="dialog[index] = false">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
                <v-toolbar-title>Section {{ index + 1 }}</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-toolbar-items>
                  <v-btn dark text :disabled="!valid" @click="refreshPanel">
                    Save
                  </v-btn>
                </v-toolbar-items>
              </v-toolbar>
              <v-card>
                <v-container class="px-10">
                  <v-card-title>Start Time</v-card-title>
                  <SectionTimePanel
                    :sectionID="section.id"
                    :video_duration="video_duration"
                    :initialTime="section.start"
                    @updateTime="updateSectionStart"
                    @updateSectionTimeFromJellyfin="updateSectionTime"
                    @loopJellyfin="loopJellyfinAtStart"
                  />
                  <v-divider></v-divider>
                  <v-card-title>End Time</v-card-title>
                  <SectionTimePanel
                    :sectionID="section.id"
                    :video_duration="video_duration"
                    :initialTime="section.end"
                    @updateTime="updateSectionEnd"
                    @updateSectionTimeFromJellyfin="updateSectionTime"
                    @loopJellyfin="loopJellyfinAtEnd"
                  />

                  <v-divider></v-divider>
                  <v-card-title>Topics</v-card-title>

                  <!-- i think the :topics below is incorrect 10/9/24 -->
                  <SectionTopicsPanel
                    :topics="section.topics"
                    :item="section"
                    @addTopic="addTopic"
                    @removeTopic="removeTopic"
                  />

                  <v-divider></v-divider>
                  <v-card-title>Musical</v-card-title>
                  <BeatsInfo />
                  <ArtistsInfo />
                </v-container>
              </v-card>
            </v-dialog>
          </v-row>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
    <div class="text-center">
      <v-snackbar
        v-model="snackbar"
        :timeout="timeout"
        absolute
        centered
        left
        :color="color"
        elevation="24"
        class="alertmessage"
      >
        {{ text }}

        <template v-slot:action="{ attrs }">
          <v-btn color="blue" text v-bind="attrs" @click="snackbar = false">
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      video_duration: 0,
      dialog: {},
      slides: 0,
      // no form implemented yet
      valid: true,
      snackbar: false,
      text: "My timeout is set to 2000.",
      color: "info",
      timeout: 2000,
    };
  },
  created() {
    console.log("Section Selector created", this.sectionItems);
  },
  methods: {
    addTopic(args) {
      this.add_item(args);
    },

    removeTopic(args) {
      this.remove_item(args);
    },

    createSectionAtJellyfin(start_or_end) {
      console.log("Creating section at jellyfin", start_or_end);
      const args = {
        start_or_end: start_or_end,
      };
      this.create_section_from_jellyfin(args);
    },

    updateSectionTime(section, start_or_end) {
      console.log("Updating times", section, start_or_end);
      const args = {
        section: section,
        start_or_end: start_or_end,
      };
      // python function
      this.update_section_from_jellyfin(args);
    },

    removeSection(section_id) {
      console.log("Deleted section", section_id);
      const sectionIndex = this.sectionItems.findIndex(
        (item) => item.id === section_id
      );
      if (sectionIndex !== -1) {
        this.sectionItems.splice(sectionIndex, 1);
      }
      const args = {
        section_id: section_id,
      };
      this.delete_section(args);
      this.refreshPanel();
    },

    loopJellyfinAtStart(value) {
      this.loop_jellyfin(value);
    },
    loopJellyfinAtEnd(value) {
      this.loop_jellyfin(value);
    },

    updateSectionStart(section_id, new_time) {
      console.log("Updating times", section_id);
      const args = {
        item_id: section_id,
        start: new_time,
      };
      console.log("Args", args);
      this.update_times(args);
    },
    updateSectionEnd(section_id, new_time) {
      console.log("Updating times", section_id);
      const args = {
        item_id: section_id,
        end: new_time,
      };
      this.update_times(args);
    },
    createTrack(section_id) {
      console.log("Creating track", section_id);
      const args = {
        section_id: section_id,
      };
      this.create_track(args);
    },

    createTrack2(args) {
      console.log("Creating track", args);
      this.text = "Creating track: " + args.title;
      this.snackbar = true;
      this.color = "success";
      this.create_track(args);
    },
    createLyricsFile(args) {
      console.log("Creating lyrics file");
      this.text = "Creating lyrics file";
      this.snackbar = true;
      this.color = "success";
      this.create_lyrics_file(args);
    },

    deleteLyricsFile(args) {
      console.log("Deleting lyrics file");
      this.text = "Deleting lyrics file";
      this.snackbar = true;
      this.color = "warning";
      this.delete_lyrics_file(args);
    },
    removeTrack(args) {
      console.log("Removing track", args);
      this.text = "Removing track id: " + args;
      this.snackbar = true;
      this.color = "warning";
      this.remove_track(args);
    },
    prettyTime(time) {
      return new Date(time * 1000).toISOString().substr(11, 8);
    },
    durationString(duration) {
      const hrs = ~~(duration / 3600);
      const mins = ~~((duration % 3600) / 60);
      const secs = ~~duration % 60;
      let ret = "";
      if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
      }

      ret += "" + mins + ":" + (secs < 10 ? "0" : "");
      ret += "" + secs;

      return ret;
    },
    logIt(args) {
      console.log("Logging", args);
    },
    refreshPanel() {
      console.log("Refreshing panel");
      this.dialog[this.slides] = false;
      this.refresh_panel();
    },
    constructTrackTitle(section) {
      const topicString = section.topics.map(({ text }) => text).join(", ");

      if (section.topics.length == 0) {
        return "";
      }
      if (topicString.length > 40) {
        return topicString.substring(0, 40) + "...";
      } else {
        return topicString;
      }
    },
    createAudioFile(args) {
      this.create_audio_file(args);
      this.text = "Creating audio file";
      this.snackbar = true;
      this.color = "success";
    },
    deleteAudioFile(args) {
      this.delete_audio_file(args);
      console.log("Deleting audio file in parent");
      this.text = "Deleting audio file";
      this.snackbar = true;
      this.color = "warning";
    },
  },
  computed: {
    sectionRange() {
      const selected = this.sectionItems[this.slides];
      if (selected === undefined) {
        return [];
      }
      return [selected.start / 1000, selected.end / 1000];
    },
    computedDefaultTrackTitle() {
      return this.constructTrackTitle(this.sectionItems[this.slides]);
    },
  },
};
</script>
<style>
.border4 {
  border: 4px solid var(--primary);
}
.alertmessage {
  font-size: 1.8em;
}
.tracknumber {
  font-family: "LogoFont";
  text-decoration: none;
  color: var(--primary);
  font-size: 1.4em;
  font-weight: 800;
  padding: 0.1em;

  margin-bottom: 0px;
}
</style>
