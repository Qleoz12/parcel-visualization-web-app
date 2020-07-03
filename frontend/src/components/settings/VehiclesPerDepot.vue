<template>
    <v-expansion-panel>
        <v-expansion-panel-header class="body-1">Max vehicles per depot</v-expansion-panel-header>
        <v-expansion-panel-content>
            <v-card
                    v-for="(depot,i) in localData"
                    :key="i"
                    style="width:100%;"
            >
                <v-card-text>Depot {{depot.id}}</v-card-text>
                <v-simple-table>
                    <td>
                        <v-slider
                                v-model="depot.vehicles.length"
                                class="align-center"
                                :max="vehiclesMax"
                                :min="vehiclesMin"
                                hide-details
                                @change="vehiclesDepot()"
                                :key="refresh"
                        >
                            <template v-slot:append>
                                <v-text-field
                                        v-model="depot.vehicles.length"
                                        class="mt-0 pt-0"
                                        hide-details
                                        single-line
                                        type="number"
                                        style="width: 40px"
                                        @click="vehiclesDepot()"
                                ></v-text-field>
                            </template>
                        </v-slider>
                    </td>
                    <td>
                        <v-card-actions class="justify-center">
                            <v-btn @click="applyToAllDepots(depot.vehicles.length)" color="warning lighten-1" style="width:150px;">Apply to all</v-btn>
                        </v-card-actions>
                    </td>
                </v-simple-table>
            </v-card>
        </v-expansion-panel-content>
    </v-expansion-panel>
</template>

<script>
    import settings_process from "./settings_process";

    export default {
        name: "VehiclesPerDepot",
        props: {
            data: Array,
            vehicles: Array,
            depots: Array
        },
        data: () => ({
            vehiclesMin: 0,
            vehiclesMax: 20,
            localData: null,
            localVehicles: null,
            localDepots: null,
            refresh: -1
        }),
        methods: {
            vehiclesDepot() {
                let param = [];
                this.localData.forEach(dep => {
                    param.push({id: dep.id, vehicles: dep.vehicles.length});
                });
                this.changeVehiclesPerDepot(param);
            },
            applyToAllDepots(vehicles) {
                let param = []
                this.localData.forEach(dep => {
                    param.push({id: dep.id, vehicles: vehicles});
                });
                this.changeVehiclesPerDepot(param);
            },
            countCurrent() {
                let res = {};
                this.localDepots.forEach(d => {
                    res[d.id] = 0;
                });

                this.localVehicles.forEach(v => {
                    res[v.depot] = res[v.depot] +1;
                });
                return res;
            },
            removeVehicles(depot, diff) {
                let newV = [];
                this.localVehicles.reverse().forEach(v => {
                    if (v.depot === depot && diff < 0) {
                        diff += 1;
                    } else {
                        newV.push(v);
                    }
                });
                newV.reverse();
                this.localVehicles = newV;
            },
            addVehicles(depot, diff) {
                let maxID = 0;
                this.localVehicles.forEach(v => {
                    maxID = (v.id > maxID) ? v.id : maxID;
                });
                for (let i = 0; i < diff; i++) {
                    maxID += 1;
                    this.localVehicles.push({"id": maxID, "depot": depot, "capacity": 10});
                }
            },
            changeVehiclesPerDepot(param) {
                let previous = this.countCurrent();
                param.forEach(dep => {
                    const diff = dep.vehicles - previous[dep.id];
                    if (diff < 0) {
                        this.removeVehicles(dep.id, diff);
                    } else if (diff > 0) {
                        this.addVehicles(dep.id, diff);
                    }
                });
                this.loadDepotsVehicles();
            },
            loadDepotsVehicles() {
                this.localData = settings_process.loadDepotsAndVehicles(this.localVehicles, this.localDepots);
                this.refresh-=1;
                this.sendToParent();
            },
            sendToParent() {
                this.$emit('update', this.localData, this.localVehicles, this.localDepots);
            }
        },
        mounted() {
            this.localData = this.data;
            this.localVehicles = this.vehicles;
            this.localDepots = this.depots;
        }
    }
</script>

<style scoped>
    td:first-child {
        width:95%;
    }
</style>
