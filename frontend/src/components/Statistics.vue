<template>
    <v-container fluid>
        <v-card class="mb-4">
            <v-toolbar flat>
                <v-toolbar-title>Statistics</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="toggleFullScreenStatistics()">
                    <v-icon v-show="sideBar">fa-expand</v-icon>
                    <v-icon v-show="!sideBar">fa-compress</v-icon>
                </v-btn>
            </v-toolbar>
        
        <v-tabs v-model="algorithm" :vertical="sideBar" :grow="sideBar">
            <v-tab
                v-for="(algorithm, i) in algorithms"
                v-bind:key="i"
            >{{ algorithm.name }}
            </v-tab>
            <v-tab :key="2">
                Boxplots
            </v-tab>
            <v-tab v-show="algorithms.length > 1" :key="3">
                Compare Algorithms
            </v-tab>
            
        </v-tabs>
    </v-card>
        <v-tabs-items v-model="algorithm">
            <v-tab-item
                v-for="(algorithm, i) in algorithms"
                v-bind:key="i"
            >
                <v-card v-if="sideBar">
                    <div class="body-2 pa-4">
                        The {{ algorithm.name }} generated {{ getRoutes(algorithm).length }} routes for {{ getPackageCount(algorithm) }} packages.
                        The cumulative distance covered is {{ getTotalDistance(getRoutes(algorithm)) }} Kilometers.
                        The cumulative elapsed time is {{ getTotalTime(getRoutes(algorithm)) }}, where the longest route takes {{ getLongestTime(getRoutes(algorithm)) }}.
                    </div>
                    <v-spacer/>
                    <v-list dense>
                        <v-list-item>
                            <DeliveryTruckList :algorithm="algorithm" :colors="colors"/>
                        </v-list-item>
                        <v-list-item>
                            <ChartList side-bar :algorithm="algorithm"/>
                        </v-list-item>
                    </v-list>
                </v-card>
                <ChartList v-else :algorithm="algorithm"/> 
            </v-tab-item>
            <v-tab-item :key="2">
                <box-plot-chart-list :side-bar="sideBar" :algorithms="algorithms"/>
            </v-tab-item>
            <v-tab-item :key="3">
                <comparison-chart-list :side-bar="sideBar" :algorithms="algorithms"/>
            </v-tab-item>
        </v-tabs-items>
    </v-container>
</template>

<script>
    import DeliveryTruckList from "./DeliveryTruckList";
    import BoxPlotChartList from "./BoxPlotChartList";
    import ChartList from "./ChartList";
    import ComparisonChartList from "./ComparisonChartList";

    export default {
        name: "Statistics",
        props: {
            algorithms: Array,
            compare: Boolean,
            sideBar: {
                type: Boolean,
                default: false
            }
        },
        components: {
            DeliveryTruckList,
            BoxPlotChartList,
            ChartList,
            ComparisonChartList,
        },
        data: () => ({
            algorithm: null,
            routes: null,
            colors: ['#ef5675', '#ffa600', '#ffa600', '#444e86', '#003f5c', '#955196']
        }),
        methods: {
            getRoutes(alg) {
                return alg.geojson.features.filter(x => x.properties.type === "route");
            },
            getTotalDistance(routes) {
                // Sum up the distances of all the routes, convert to km and round to 1 decimal
                return (routes.reduce((acc, cur) => acc + cur.properties.distance, 0) / 1000).toFixed(1);
            },
            getPackageCount(alg) {
                // Count the total amount of packages being delivered
                return alg.geojson.features.filter(x => x.properties.type === "delivery").length;
            },
            getTotalTime(routes) {
                // Count total time spent delivering the packages
                let time = routes.reduce((acc, cur) => acc + (cur.properties.duration_h*60)+cur.properties.duration_m, 0);
                return Math.floor(time / 60) + " hours and " + Math.round((time / 60) % 60) + " minutes";
            },
            getLongestTime(routes) {
                let longestTime = routes.reduce((acc, cur) => acc = Math.max((cur.properties.duration_h*60)+cur.properties.duration_m, acc), 0)
                return Math.floor(longestTime / 60) + " hours and " + Math.round((longestTime / 60) % 60) + " minutes";
            },
            toggleFullScreenStatistics() {
                if (this.sideBar) {
                    this.$emit('enter-full-screen-statistics');
                } else {
                    this.$emit('exit-full-screen-statistics');
                }
            }
        }
    }
</script>

<style scoped>
    .v-tab {
        justify-content: start;
    }
</style>
