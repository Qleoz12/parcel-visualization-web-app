<template>
    <v-app>
        <!-- Right side-bar menu -->
        <v-navigation-drawer
        v-if="statisticsMode === false"
        v-bind:width="500"
        v-model="drawerRight"
        mobile-break-point="767"
        app
        right
        clipped
        >
            <!-- Display the statistics a tabbed list in the side bar -->
            <Statistics
                v-if="geoLoaded"
                side-bar
                :key="refresh"
                :compare="compareMode"
                :algorithms="selectedAlgorithms"
                :colors="chartColors"
                v-on:enter-full-screen-statistics="statisticsMode = true"
            />
        </v-navigation-drawer>

        <!-- Left side-bar menu -->
        <v-navigation-drawer
            v-bind:width="300"
            v-model="drawerLeft"
            mobile-break-point="767"
            app
            left
            clipped
        >
            <v-container  fluid class="pa-6 align-space-between">
                <v-card flat class="mb-4">
                    <v-row>
                        <v-col cols="12" class="pb-1 pt-0">
                            <v-btn color="primary lighten-1" @click="openSettings" style="width:100%;">
                                <v-icon left>mdi-cog</v-icon>Settings
                            </v-btn>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12">
                            <v-toolbar-title>Select algorithm</v-toolbar-title>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12">
                            <!-- Dropdown button for selecting algorithm -->
                            <v-select
                                :items="algorithms"
                                item-text="text"
                                item-value="value"
                                v-model="defaultSelected"
                                hide-details
                                bottom
                                solo
                                v-bind:return-object="true"
                                @change="changeAlgorithm($event)"
                            ></v-select>
                        </v-col>
                    </v-row>
                    <v-row>
                        <!-- Switch for comparison mode -->
                        <v-col cols="12" class="pt-1">
                            <v-switch hide-details v-model="switchVal" :label="`Comparison mode`" @change="changeMode()" color="primary" style="width:100%" class="mt-2"></v-switch>
                        </v-col>
                    </v-row>
                    <v-row v-show="switchVal">
                        <v-col cols="12">
                            <!-- Dropdown button for selecting second algorithm -->
                            <v-select
                                :class="selectClass"
                                :items="secondAlgorithms"
                                item-text="text"
                                item-value="value"
                                v-model="defaultSelectedCompare"
                                hide-details
                                bottom
                                solo
                                v-bind:return-object="true"
                                @change="changeSecondAlgorithm($event)"
                            ></v-select>
                        </v-col>
                    </v-row>
                </v-card>
                <v-divider></v-divider>
                <v-card flat class="mb-4">
                    <v-row>
                        <v-col cols="12">
                            <v-toolbar-title>Overview</v-toolbar-title>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" class="pa-0">
                            <!-- Component for showing the properties of the selected algorithm(s), such as name, version, etc. -->
                            <PropertiesTable v-if="algorithmLoaded" :algorithms="selectedAlgorithms" :key="refresh"/>
                        </v-col>
                    </v-row>
                </v-card>
                <v-divider></v-divider>
                <v-card flat>
                    <v-row>
                        <v-col cols="12">
                            <v-toolbar-title>Simulation manager</v-toolbar-title>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" class="pt-0 pb-0">
                            <!-- Slider to control the timeline of the simulation -->
                            <v-slider
                                v-model="position"
                                class="align-center"
                                thumb-label
                                prepend-icon="mdi-map-marker-right"
                                track-color="light"
                                color="primary"
                                @change="changePosition"
                                :min="positionMin"
                                :max="positionMax"
                                hide-details
                            >
                                <template v-slot:thumb-label="{ value }">
                                    {{ value + "%" }}
                                </template>
                            </v-slider>
                        </v-col>
                    </v-row>
                    <!-- Simulation controls (play, pause, fast-forward, reset, etc.) -->
                    <v-row justify-center dense>
                        <v-col cols="3" align="center">
                            <v-btn rounded block color="primary lighten-1" @click="playPauseSimulation()">
                                <span v-show="animationPlaying"><v-icon medium>mdi-pause</v-icon></span>
                                <span v-show="!animationPlaying"><v-icon medium>mdi-play</v-icon></span>
                            </v-btn>
                        </v-col>
                        <v-col cols="3" align="center">
                            <v-btn rounded block color="secondary lighten-1" @click="resetSimulation()">
                                <v-icon>mdi-undo</v-icon>
                            </v-btn>
                        </v-col>
                        <v-col cols="6">
                            <v-select
                                v-model="speed"
                                :items="speeds"
                                @change="changeSimulationSpeed()"
                                item-value="value"
                                item-text="text"
                                label="Speed"
                                prepend-inner-icon="mdi-play-speed"
                                menu-props="auto"
                                dense
                                solo
                                rounded
                                single-line
                            />
                        </v-col>
                    </v-row>
                </v-card>
            </v-container>
        </v-navigation-drawer>

        <!-- Creates the app bar at the top of the application -->
        <v-app-bar
            app
            clipped-right
            clipped-left
            color="blue"
            dark
        >
            <v-tooltip right>
                <template v-slot:activator="{ on }">
                    <v-btn
                        icon
                        @click.stop="drawerLeft = !drawerLeft"
                        v-on="on"
                    >
                        <v-icon>mdi-information</v-icon>
                    </v-btn>
                </template>
                <span>Control panel</span>
            </v-tooltip>
            <v-spacer/>
            <v-toolbar-title>Parcel Delivery Algorithm Visualization</v-toolbar-title>
            <v-spacer/>
            <v-tooltip left>
                <template v-slot:activator="{on}">
                    <v-btn
                        icon
                        @click.stop="drawerRight = !drawerRight"
                        v-on="on"
                      >
                        <v-icon>mdi-finance</v-icon>
                    </v-btn>
                </template>
                <span>Algorithm statistics</span>
            </v-tooltip>
        </v-app-bar>

        <!-- Main content container -->
        <v-content>
            <!-- Shows the map(s), unless in statistics mode -->
            <v-container fill-height fluid v-if="(!statisticsMode && geoLoaded)" pa-0>
                <v-layout style="position: absolute">
                    <v-btn class="mt-5" color="tertiary" @click.native="randomize()" style='left: 50px; z-index: 5;'>
                        <span class="mr-3"><v-icon>mdi-map-marker-multiple</v-icon></span>
                        randomize
                    </v-btn>
                </v-layout>
                <Maps
                    :algorithms="selectedAlgorithms"
                    :key="refresh"
                    :compare="compareMode"
                    :maxDuration="maxDur"
                />
            </v-container>
            <!-- If in statistics mode, show the full-screen statistics screen -->
            <Statistics
                v-else-if="geoLoaded"
                :key="refresh"
                :compare="compareMode"
                :algorithms="selectedAlgorithms"
                :colors="chartColors"
                v-on:exit-full-screen-statistics="statisticsMode = false"
            />
            <!-- Show settings screen menu when activated -->
            <Settings v-if="algorithmLoaded" ref="settings" :algorithms="JSON.parse(JSON.stringify(selectedAlgorithms))"
                :selectAlgorithms="algorithms" :input="input" :default="defaultSelected"
                @saveOrders="saveGeneralSettings" @saveVehicles="saveAlgSettings" @saveScenario="saveScenarioSettings"
                style="z-index:999;" :key="refresh+1"
            />
            <!-- Loading spinner -->
            <v-overlay :value="!geoLoaded" style="z-index: 999">
                <v-progress-circular indeterminate size="64"></v-progress-circular>
            </v-overlay>
        </v-content>

        <v-footer
            app
            color="blue"
            class="white--text"
        >
            <span>Almende B.V.</span>
            <v-spacer/>
            <span>&copy; 2020</span>
        </v-footer>
    </v-app>
</template>


<script>
    import PropertiesTable from './PropertiesTable';
    import Maps from './Maps';
    import Statistics from "./Statistics";
    import Settings from "./Settings";

    export default {
        components: {
            Statistics,
            PropertiesTable,
            Maps,
            Settings
        },
        data: () => ({
            statisticsMode: false,
            routes: [],
            vehicles: [],
            drawerLeft: null,
            drawerRight: null,
            speeds: [
                {text:   "1x", value:   1},
                {text:  "10x", value:  10},
                {text:  "60x", value:  60},
                {text: "100x", value: 100},
                {text: "200x", value: 200},
                {text: "400x", value: 400},
                {text: "600x", value: 600}
            ],
            maxDur: null,
            speed: 100,
            simulationInterval: null,
            position: 0,
            positionMin: 0,
            positionMax: 100,
            animationPlaying: false,
            geoLoaded: false,
            chartColors: ["#ef5675","#ffa600","#ffa600","#444e86","#003f5c","#955196"],
            mapColors: ["#f44336", "#4caf50", "#2196f3", "#ff9800", "#9c27b0", "#795548"],
            defaultSelected: {},
            algorithms: [],
            defaultSelectedCompare: {'value': 999, 'text': "Select algorithm"},
            secondAlgorithms: [{'value': 999, 'text': "Select algorithm"}],
            algorithmLoaded: false,
            refresh: 0,
            compareMode: false,
            switchVal: false,
            selectClass: "singleSelect",
            selectedAlgorithms: [],
            orders: [],
            input: null,
            defaultVehicles: null,
            defaultDepots: null,
            scenario: null
        }),
        mounted() {
            this.load();
            this.$root.$on('resetSimulation', this.resetSim);
        },
        methods: {
            async load() {
                this.axios
                    .get(process.env.VUE_APP_BACKEND_URI + '/settings/input_variables')
                    .then(result => {
                        this.input = result.data.input[0];
                        this.defaultVehicles = result.data.vehicles;
                        this.defaultDepots = result.data.depots;
                        this.orders = result.data.deliveries;
                        this.scenario = result.data.scenario;
                        this.axios
                            .get(process.env.VUE_APP_BACKEND_URI + '/compare/algorithms')
                            .then(response => {
                                this.fillSelect(response.data);
                            });
                    });
            },
            fillSelect(data) {
                data.forEach(item => {
                    this.algorithms.push({'value': item.key, 'text': item.name});
                    this.secondAlgorithms.push({'value': item.key, 'text': item.name});
                    if (item.default === 1) {
                        this.defaultSelected = {'value': item.key, 'text': item.name};
                        this.selectedAlgorithms.push({id: item.key, name: item.name, geojson: null, vehicles: null,
                            changedVehicles: this.defaultVehicles, depots: this.defaultDepots, scenario: this.scenario})
                        this.algorithmLoaded = true;
                    }
                });
                this.loadScreen(0);
            },
            async randomize() {
                this.geoLoaded = false;
                this.axios.post(process.env.VUE_APP_BACKEND_URI + '/orders/randomize', {}, {
                    params: {
                        orders: this.input.orders,
                        depot_radius: this.input.depotRadius
                    }
                }).then(async response => {
                    this.orders = response.data;
                    for (let i = 0; i < this.selectedAlgorithms.length; i++) {
                        await this.loadScreen(i);
                    }
                }).catch(error => {
                  if (error.response.status === 508) {
                      this.geoLoaded = true;
                      alert("Random order generation failed. Try changing settings like the depot radius, depot " +
                          "locations or order number. If the failure persists, contact the admin.")
                  }
              });
            },
            async loadScreen(index) {
                this.geoLoaded = false;
                this.animationPlaying = false;
                this.position = 0;
                this.speed = 100;
                let algorithm = this.selectedAlgorithms[index];
                this.axios.post(process.env.VUE_APP_BACKEND_URI + '/map/geojson', {
                    deliveries: this.orders,
                    vehicles: algorithm.changedVehicles,
                    scenario: algorithm.scenario
                }, {
                    params: {
                        algorithm: algorithm.id
                    }
                }).then(response => {
                    this.selectedAlgorithms[index].geojson = this.insertColors(response.data.geojson);
                    this.selectedAlgorithms[index].vehicles = this.vehiclesFromRoutes(response.data.geojson.features.filter(x => x.properties.type === "route"));
                    this.maxDur = this.maxDuration();
                    this.refresh += 1;
                    this.geoLoaded = true;
                });
            },
            /**
             * Plays or pauses the animation of the MovingMarkers.
             */
            playPauseSimulation() {
                if (this.animationPlaying) {
                    window.clearInterval(this.simulationInterval);
                    this.simulationInterval = null;
                    this.$root.$emit('pauseMovingMarker');
                    this.animationPlaying = false;
                } else {
                    this.startInterval();
                    this.$root.$emit('startMovingMarker');
                    this.animationPlaying = true;
                }
            },
            startInterval() {
                this.simulationInterval = window.setInterval(() => {
                    this.position++;
                    if (this.position === 100) {
                        window.clearInterval(this.simulationInterval);
                    }
                }, this.maxDur / this.speed / 100);
            },
            updateInterval() {
                if (this.animationPlaying) {
                    window.clearInterval(this.simulationInterval);
                    this.startInterval();
                }
            },
            resetSim(dur) {
                if (dur === this.maxDur) this.resetSimulation();
            },
            /**
             * Resets the MovingMarkers to the initial location.
             */
            resetSimulation() {
                this.$root.$emit('resetMovingMarker');
                window.clearInterval(this.simulationInterval);
                this.simulationInterval = null;
                this.position = 0;
                this.animationPlaying = false;
            },
            /**
             * Informs the MovingMarkers that the speed should change.
             */
            changeSimulationSpeed() {
                this.$root.$emit('speedChangeMovingMarker', this.speed);
                this.updateInterval();
            },
            /**
             * Informs the MovingMarkers that the position should change.
             */
            changePosition() {
                this.$root.$emit('positionChangeMovingMarker', this.position, this.animationPlaying);
            },
            /**
             * Returns the duration of the longest route.
             */
            maxDuration: function () {
                let dur = 0;
                let maxDur = 0;
                let allRoutes = null;
                let delays = null;
                let route = null;
                for (let i = 0; i < this.selectedAlgorithms.length; i++) {
                    allRoutes = this.selectedAlgorithms[i].geojson.features.filter((feature) => feature.properties.type === 'route');
                    for (let route_i in allRoutes) {
                        route = allRoutes[route_i];
                        dur = (route.properties.duration_h * 60) + route.properties.duration_m;
                        delays = this.selectedAlgorithms[i].geojson.features.filter((feature) => (feature.properties.type === 'delayed' && feature.properties.route_number === route.properties.number));
                        delays.forEach((delay) => {
                            dur += delay.properties.duration;
                        });
                        if (maxDur < dur) {
                            maxDur = dur;
                        }
                    }
                }
                return maxDur * 60000;
            },
            vehiclesFromRoutes: function (routes) {
                let vehicles = [];
                routes.forEach(route => {
                    let vehicle = {
                        'id': route.properties.number-1,
                        'name': 'Vehicle ' + route.properties.number,
                        'color': this.mapColors[(route.properties.number-1) % this.mapColors.length]
                    };
                    vehicles.push(vehicle);
                });
                return vehicles;
            },
            updateNames() {
                if (this.selectedAlgorithms.length>1) {
                    if (this.selectedAlgorithms[0].id === this.selectedAlgorithms[1].id) {
                        this.selectedAlgorithms[0].name += " (1)";
                        this.selectedAlgorithms[1].name += " (2)";
                    } else if (this.selectedAlgorithms[0].name.includes(")")) {
                        this.selectedAlgorithms[0].name = this.selectedAlgorithms[0].name.substr(0,this.selectedAlgorithms[0].name.length - 4);
                    } else if (this.selectedAlgorithms[1].name.includes(")")) {
                        this.selectedAlgorithms[1].name = this.selectedAlgorithms[0].name.substr(0,this.selectedAlgorithms[0].name.length - 4);
                    }
                } else if (this.selectedAlgorithms[0].name.includes(")")) {
                    this.selectedAlgorithms[0].name = this.selectedAlgorithms[0].name.substr(0,this.selectedAlgorithms[0].name.length - 4);
                }
            },
            insertColors(geojson) {
                geojson.features.forEach(f => {
                    if (f.properties.type === "route") {
                        f.properties.style = {
                            color: this.mapColors[(f.properties.number - 1) % this.mapColors.length],
                            weight: 3
                        };
                    } else if (f.properties.type === "delivery") {
                        f.properties.style = {
                            icon: "fa-box-open",
                            color: this.mapColors[(f.properties.route_number - 1) % this.mapColors.length],
                            markerColor: "white"
                        };
                        f.properties.single_route.properties.style = {
                            color: "black",
                            opacity: 0.3,
                            weight: 9
                        }
                    } else if (f.properties.type === "depot" || f.properties.type === "start") {
                        f.properties.style = {
                            icon: "fa-warehouse",
                            color: "black",
                            markerColor: "white"
                        };
                    } else if (f.properties.type === "handover") {
                        f.properties.style = {
                            icon: "fa-people-carry",
                            color: this.mapColors[(f.properties.route_number - 1) % this.mapColors.length],
                            markerColor: "white"
                        };
                    } else if (f.properties.type === "pickup") {
                        f.properties.style = {
                            icon: "fa-download",
                            color: this.mapColors[(f.properties.route_number - 1) % this.mapColors.length],
                            markerColor: "white"
                        };
                    } else if (f.properties.type === "mode_change") {
                        f.properties.style = {
                            icon: "fa-sync",
                            color: this.mapColors[(f.properties.route_number - 1) % this.mapColors.length],
                            markerColor: "white"
                        };
                    }
                });
                return geojson;
            },
            changeAlgorithm(event) {
                this.selectedAlgorithms[0] = {
                    id: event.value, name: event.text, geojson: null, vehicles: null,
                    changedVehicles: this.defaultVehicles, depots: this.defaultDepots, scenario: this.scenario
                };
                this.updateNames();
                this.geoLoaded = false;
                this.loadScreen(0);
                this.refresh += 1;
            },
            changeMode() {
                if (this.switchVal) {
                    this.selectClass = "compareSelect";
                } else {
                    this.animationPlaying = false;
                    this.position = 0;
                    this.speed = 100;
                    this.defaultSelectedCompare = {'value': 999, 'text': "Select algorithm"};
                    this.selectClass = "singleSelect";
                    this.selectedAlgorithms.splice(1, 1);
                    if (this.compareMode) {
                        this.compareMode = false;
                        this.updateNames();
                        this.maxDur = this.maxDuration();
                        this.refresh += 1;
                    }
                }
            },
            changeSecondAlgorithm(event) {
                if (event.value === 999) {
                      this.switchVal = false;
                      this.changeMode();
                      this.compareMode = false;
                } else {
                    this.selectedAlgorithms.splice(1, 1);
                    const vSettings = this.selectedAlgorithms[0].changedVehicles;
                    const depSettings = this.selectedAlgorithms[0].depots;
                    const scenSettings = this.selectedAlgorithms[0].scenario;
                    this.selectedAlgorithms.push({
                        id: event.value, name: event.text, geojson: null, vehicles: null,
                        changedVehicles: vSettings, depots: depSettings, scenario: scenSettings
                    });
                    this.updateNames();
                    this.geoLoaded = false;
                    this.compareMode = true;
                    this.loadScreen(1);
                    this.refresh += 1;
                }
            },
            openSettings: function () {
                this.$refs.settings.openDialog();
            },
            saveAlgSettings(vs, ds, alg, scenario) {
                this.selectedAlgorithms[alg].changedVehicles = vs;
                this.selectedAlgorithms[alg].depots = ds;
                this.selectedAlgorithms[alg].scenario = scenario;
                this.loadScreen(alg);
            },
            saveGeneralSettings(orders, depotRadius, randomize) {
                this.input.orders = orders;
                this.input.depotRadius = depotRadius;
                if (randomize) this.randomize();
            },
            saveScenarioSettings(scen, alg) {
                this.selectedAlgorithms[alg].scenario = scen;
                this.loadScreen(alg);
            }
        }
    }
</script>

<style scoped>
    .singleSelect {
        display: none;
    }

    .compareSelect {
        display: block;
    }
</style>
