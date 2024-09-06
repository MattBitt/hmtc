<template>
        <v-sheet class="mt-6">
                <!-- Timer Display -->

                <v-row class="d-flex justify-center">
                        <!-- Hours Digit -->
                        <v-responsive max-width="50" class="digit-label mr-1 ml-4">
                                {{ String(timestamp.hour).padStart(2, "0") }}
                        </v-responsive>
                        <!-- Minutes Digit -->
                        <v-responsive max-width="50" class="digit-label mx-0">
                                {{ String(timestamp.minute).padStart(2, "0") }}
                        </v-responsive>

                        <!-- Seconds Digit -->
                        <v-responsive max-width="50" class="digit-label mr-4 ml-1">
                                {{ String(timestamp.second).padStart(2, "0") }}
                        </v-responsive>

                </v-row>

        </v-sheet>
</template>

<style>
.digit-label {
        font-size: 30px;
        background-color: var(--dark) !important;
        color: var(--on-dark) !important;
        text-align: center;
        padding: 4px;

}
</style>

<script>
export default {
        data: () => ({
                timestamp: {
                        id: 456,
                        timestamp: 456,
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