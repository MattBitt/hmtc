<template>
        <v-container>
                <v-row>{{ label }}</v-row>

                <!-- Timer Display -->
                <v-sheet height="300px">
                        <v-row class="d-flex justify-center">
                                <!-- Hours Digit -->
                                <v-col class="hours"> {{ hour() }}</v-col>

                                <!-- Minutes Digit -->
                                <v-col class="minutes"> {{ minute() }}</v-col>

                                <!-- Seconds Digit -->
                                <v-col class="seconds">
                                        {{ second() }}
                                </v-col>

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
.row {

        font-weight: bold;

        border: 1px dashed black;

}

.hours {
        font-size: 30px;
        color: red !important;
        text-align: right;
}

.minutes {
        font-size: 30px;
        color: green !important;
        text-align: center;


}

.seconds {
        font-size: 30px;
        color: blue !important;
        text-align: left;
}
</style>

<script>
export default {
        data: () => ({
                label: "Blank Text",
                timestamp: {
                        id: 123,
                        timestamp: 123,
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