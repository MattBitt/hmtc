<template>
        <v-container style="">
                <v-row>{{ label }}</v-row>
                <!-- Timer Display -->
                <v-sheet height="200px">
                        <v-row class="d-flex justify-center">
                                <!-- Hours Digit -->
                                <v-responsive max-width="50" class="mx-2 py-2">
                                        <v-text-field ref="input" v-model="timestamp.hour"
                                                class="digit-input"></v-text-field>
                                </v-responsive>

                                <!-- Minutes Digit -->
                                <v-responsive max-width="50" class="mx-2 py-2">
                                        <v-text-field ref="input" v-model="timestamp.minute"
                                                class="digit-input"></v-text-field>

                                </v-responsive>

                                <!-- Seconds Digit -->
                                <v-responsive max-width="50" class="mx-2 py-2">
                                        <v-text-field ref="input" v-model="timestamp.second"
                                                class="digit-input"></v-text-field>
                                </v-responsive>
                        </v-row>
                        <v-row class="d-flex justify-center px-4 mx-10 my-2">
                                <v-btn medium @click="start_large_rewind()">
                                        <v-icon>mdi-step-backward-2</v-icon>
                                </v-btn>
                                <v-btn medium @click="start_small_rewind()">
                                        <v-icon>mdi-step-backward</v-icon>
                                </v-btn>

                                <v-btn medium @click="start_small_forward()">
                                        <v-icon> mdi-step-forward </v-icon>
                                </v-btn>
                                <v-btn medium @click="start_large_forward()">
                                        <v-icon left> mdi-step-forward-2 </v-icon>
                                </v-btn>
                        </v-row>

                        <v-row class="d-flex justify-center px-4 mx-10 my-2">
                                <v-btn medium @click="start_small_rewind()">
                                        <v-icon>mdi-content-save</v-icon>Save
                                </v-btn>
                                <v-btn medium @click="setEditMode()">
                                        <v-icon> mdi-pencil </v-icon>Revert
                                </v-btn>

                        </v-row>
                </v-sheet>
        </v-container>
</template>
<style>
.digit-input {
        font-size: 30px;
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