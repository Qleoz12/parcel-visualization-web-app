<template>
    <div>
        <v-list>
            <v-list-item class="justify-md-center" >
                <v-list-item-title class="title mt-6 align-center">Vehicle settings</v-list-item-title>
            </v-list-item>
            <v-list-item>
                <p>These settings are used during route generation. The algorithm will be reloaded with the updated
                    settings on "save".</p>
            </v-list-item>
            <v-list-item>
                <v-simple-table style="width:100%">
                    <tbody>
                    <ScenarioRow
                            v-for="(setting, i) in rows"
                            :key="i"
                            :content="setting"
                            @change="change"
                    />
                    </tbody>
                </v-simple-table>
            </v-list-item>
            <v-list-item>
                <v-expansion-panels>
                    <VehiclesPerDepot @update="update" :data="localData" :vehicles="vehicles" :depots="depots" :key="refreshVPD" />
                    <OrdersPerVehicle @update="update" :data="localData" :vehicles="vehicles" :depots="depots" :key="refreshOPV" />
                </v-expansion-panels>
            </v-list-item>
        </v-list>
        <ControlButtons :action="'reload'" :threeButtons="false" @cancel="cancel" @save="save"/>
    </div>
</template>

<script>
    import VehiclesPerDepot from "./VehiclesPerDepot";
    import OrdersPerVehicle from "./OrdersPerVehicle";
    import ControlButtons from "./ControlButtons";
    import ScenarioRow from "./ScenarioRow";
    import settings_process from "./settings_process";

    export default {
        name: "VehicleSettings",
        components: {OrdersPerVehicle, VehiclesPerDepot, ControlButtons, ScenarioRow},
        props: {
            algorithm: Object,
            index: Number
        },
        data: () => ({
            localData: [],
            vehicles: [],
            depots: [],
            initV: [],
            initD: [],
            refreshVPD: 1,
            refreshOPV: 0,
            scenario: null,
            rows: [
                {
                    id: 1,
                    title: "Vehicle cost per time step",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: false,
                    model: null
                },
                {
                    id: 2,
                    title: "Driver cost per time step",
                    min: 1,
                    max: 50,
                    disabled: true,
                    infinite: false,
                    slider: false,
                    model: null
                },
            ]
        }),
        methods: {
            update(aggrData, vs, ds) {
                this.localData = aggrData;
                this.vehicles = vs;
                this.depots = ds;
                this.refreshOPV -= 1;
            },
            cancel() {
                this.vehicles = this.initV;
                this.depots = this.initD;
                this.localData = settings_process.loadDepotsAndVehicles(this.vehicles, this.depots);
                this.refreshVPD += 1;
                this.refreshOPV -= 1;
                this.$emit('close');
            },
            save() {
                this.initV = this.vehicles;
                this.initD = this.depots;
                const modifiedV = this.updateIndices(this.vehicles.sort(this.compare));
                this.scenario.cost_vehicle = this.rows[0].model;
                this.scenario.cost_driver = this.rows[1].model;
                this.$emit('saveSettings', modifiedV, this.depots, this.index, this.scenario);
            },
            compare(a,b) {
                if (a.id < b.id) {
                    return -1;
                } else if (a.id > b.id) {
                    return 1;
                } else return 0;
            },
            updateIndices(vehicles) {
                let res = [];
                for (let i = 0; i < vehicles.length; i++) {
                    res.push({id: i+1, depot: vehicles[i].depot, capacity: vehicles[i].capacity});
                }
                return res;
            },
            change(rowId, obj) {
                this.rows.forEach(row => {
                    if (row.id === rowId) {
                        row = obj;
                    }
                });
            },
        },
        mounted() {
            this.vehicles = this.algorithm.changedVehicles;
            this.depots = this.algorithm.depots;
            this.scenario = this.algorithm.scenario;
            this.initV = this.algorithm.changedVehicles;
            this.initD = this.algorithm.depots;
            this.rows[0].model = this.algorithm.scenario.cost_vehicle;
            this.rows[1].model = this.algorithm.scenario.cost_driver;
            this.localData = settings_process.loadDepotsAndVehicles(this.vehicles, this.depots);
            this.refreshVPD += 1;
            this.refreshOPV -= 1;
        }
    }
</script>

<style scoped>

</style>
