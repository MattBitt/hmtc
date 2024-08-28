<template>
        <v-container>
                <v-row>{{ label }}</v-row>

                <!-- Timer Display -->
                <v-sheet height="250px">
                        <v-row class="d-flex justify-center">
                                <!-- Hours Digit -->
                                <v-responsive max-width="50" class="hours mx-2 py-2">
                                        {{ timestamp.hour }}
                                </v-responsive>
                                <!-- Minutes Digit -->
                                <v-responsive max-width="50" class="hours mx-2 py-2">
                                        {{ timestamp.minute }}
                                </v-responsive>

                                <!-- Seconds Digit -->
                                <v-responsive max-width="50" class="hours mx-2 py-2">
                                        {{ timestamp.second }}
                                </v-responsive>

                        </v-row>

                        <v-row class="d-flex justify-center px-4 mx-10 my-2">

                                <v-btn medium @click="setEditMode('true')">
                                        <v-icon> mdi-pencil </v-icon>
                                </v-btn>

                        </v-row>
                </v-sheet>
        </v-container>
</template>

<style>
.hours {
        font-size: 30px;
        background-color: var(--dark) !important;
        color: var(--on-dark) !important;
        text-align: center;
}

.minutes {
        font-size: 30px;
        background-color: var(--dark) !important;
        color: var(--on-dark) !important;
        text-align: center;


}

.seconds {
        font-size: 30px;
        background-color: var(--dark) !important;
        color: var(--on-dark) !important;
        text-align: center;
}
</style>

<script>
export default {
        data: () => ({
                label: "Blank Text",
                timestamp: {
                        id: 456,
                        timestamp: 456,
                        hour: 10,
                        minute: 20,
                        second: 30,
                },
                number: 0,
                numberRule: (val) => {
                        if (val < 0) return "Please enter a positive number";
                        return true;
                },
        }),
        methods: {

                hour() {
                        console.log(this.timestamp.timestamp);
                        h = Math.floor(this.timestamp.timestamp / 3600);
                        return String(h).padStart(2, "0");
                },
                minute() {
                        t = this.timestamp.timestamp - this.hour() * 3600;
                        m = Math.floor(t / 60);
                        return String(m).padStart(2, "0");
                },
                second() {
                        t = this.timestamp.timestamp - this.hour() * 3600 - this.minute() * 60;

                        s = Math.floor(t);
                        return String(s).padStart(2, "0");
                },

        },
        mounted: () => {
                console.log("mounted");
        },
        destroyed: () => {
                console.log("destroyed");
        },
        watch: {},
};
</script>