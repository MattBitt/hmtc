<template>
        <v-container style="">
                <v-row>{{ label }}</v-row>
                <!-- Timer Display -->
                <v-sheet>
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
                        hour: 10,
                        minute: 20,
                        second: 30,
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