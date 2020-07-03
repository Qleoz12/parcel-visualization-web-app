<template>
    <v-container fill-height fluid pa-0>
        <v-container fill-height fluid v-if="compare" pa-0>
            <MapView
                :geojson="algorithms[0].geojson"
                :maxDuration="maxDuration"
                :vehicle-capacity="getCapacities(algorithms[0])"
                class="compareMode"
            />
            <v-divider
                v-bind:vertical="true"
                style="z-index:99; width: 0.2%"
            />
            <MapView
                :geojson="algorithms[1].geojson"
                :maxDuration="maxDuration"
                :vehicle-capacity="getCapacities(algorithms[1])"
                class="compareMode"
            />
        </v-container>
        <MapView
            v-else
            :geojson="algorithms[0].geojson"
            :maxDuration="maxDuration"
            :vehicle-capacity="getCapacities(algorithms[0])"
            class="singleMode"
        />
    </v-container>
</template>

<script>
    import MapView from "./MapView";

    export default {
        name: "Maps",
        props: {
            algorithms: Array,
            compare: Boolean,
            maxDuration: Number
        },
        components: {
            MapView
        },
        methods: {
            /**
             * Returns the capacities of the algorithms.
             * @param {Object} algorithm The corresponding algorithm
             */
            getCapacities(algorithm) {
                let res = [];
                if (algorithm.id === 1) {
                    algorithm.geojson.features.filter((feature) => feature.properties.type === 'route').forEach(function() {
                        res.push(algorithm.scenario.capacity);
                    });
                } else {
                    for (let i = 0; i < algorithm.geojson.features.filter((feature) => feature.properties.type === 'route').length; i++) {
                        res.push(algorithm.changedVehicles[i].capacity);
                    }
                }
                return res;
            }
        }
    }
</script>

<style scoped>
    .compareMode {
        width:49.87%; /* Needs to be lower than 49.9% in order to prevent width being too large due to float imprecision*/
    }

    .singleMode {
        width:100%;
    }
</style>
