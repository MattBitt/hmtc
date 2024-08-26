<template>

        <v-container style="border: 4px solid pink">

                <v-row>{{ label }}</v-row>

                <!-- Timer Display -->
                <v-sheet height="300px">
                        <v-row class="d-flex justify-center">
                                <!-- Hours Digit -->
                                <v-responsive max-width="100">
                                        <v-text-field type="number" ref="input" :rules="[numberRule]"
                                                v-model.number="number1"></v-text-field>
                                </v-responsive>

                                <!-- Minutes Digit -->
                                <v-responsive max-width="100">
                                        <v-text-field type="number" ref="input" :rules="[numberRule]"
                                                v-model.number="number2"></v-text-field>

                                </v-responsive>

                                <!-- Seconds Digit -->
                                <v-responsive max-width="100">
                                        <v-text-field type="number" ref="input" :rules="[numberRule]"
                                                v-model.number="number3"></v-text-field>
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
<style></style>

<script>
export default {
        data: () => ({
                label: "Blank Text",
                section: {
                        id: "Section 2",
                        start: "Start 2",
                        end: "End 2",
                        is_first: false,
                        is_last: false,
                        section_type: "intro",
                        duration: 92287,
                },
                number1: 15,
                number2: 23,
                number3: 38,
                mytext: "Initial",
                edit_mode: false,
                edit_mode_end: false,
                editing: false,
                number: 0,
                numberRule: (val) => {
                        if (val < 0) return "Please enter a positive number";
                        return true;
                },
        }),
        methods: {
                hour() {
                        h = Math.floor(this.section.duration / 3600);
                        return String(h).padStart(2, "0");
                },
                minute() {
                        t = this.section.duration - this.hour() * 3600;
                        m = Math.floor(t / 60);
                        return String(m).padStart(2, "0");
                },
                second() {
                        t = this.section.duration - this.hour() * 3600 - this.minute() * 60;

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