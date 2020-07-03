<template>
    <v-expansion-panel>
        <v-expansion-panel-header class="body-1">Max orders per vehicle</v-expansion-panel-header>
        <v-expansion-panel-content
                v-for="(depot,i) in localData"
                :key="i"
        >
            <v-card-title class="body-1">Depot {{depot.id}}</v-card-title>
            <v-card
                    v-for="(vehicle,i) in depot.vehicles"
                    :key="i"
                    style="width:100%;"
            >
                <v-card-text>Vehicle {{i+1}}</v-card-text>
                <v-slider
                        v-model="vehicle.capacity"
                        class="align-center"
                        :max="ordersMax"
                        :min="ordersMin"
                        hide-details
                        @click="ordersVehicle()"
                >
                    <template v-slot:append>
                        <v-text-field
                                v-model="vehicle.capacity"
                                class="mt-0 pt-0"
                                hide-details
                                single-line
                                type="number"
                                style="width: 60px"
                                @click="ordersVehicle()"
                        ></v-text-field>
                    </template>
                </v-slider>
                <v-card-actions class="justify-center">
                    <v-btn class="justify-center" @click="applyToDepot(depot.id, vehicle.capacity)" color="warning lighten-1" style="width:150px;">Apply to depot</v-btn>
                    <v-btn class="justify-center" @click="applyToAllVehicles(vehicle.capacity)" color="warning lighten-1" style="width:150px;">Apply to all</v-btn>
                </v-card-actions>
            </v-card>
        </v-expansion-panel-content>
    </v-expansion-panel>
</template>

<script>
    import settings_process from "./settings_process";

    export default {
        name: "OrdersPerVehicle",
        props: {
            data: Array,
            vehicles: Array,
            depots: Array
        },
        data: () => ({
            ordersMin: 1,
            ordersMax: 50,
            localData: [],
            localVehicles: null,
            localDepots: null
        }),
        methods: {
            ordersVehicle() {
                let param = [];
                this.localData.forEach(dep => {
                    dep.vehicles.forEach(v => {
                        param.push({id: v.id, depot: dep.id, capacity: v.capacity});
                    });
                });
                this.changeOrdersPerVehicle(param);
            },
            changeOrdersPerVehicle(param) {
                this.localVehicles = param;
                this.loadDepotsVehicles()
            },
            applyToDepot(depot, capacity) {
                let param = [];
                this.localData.forEach(dep => {
                    if (dep.id === depot) {
                        dep.vehicles.forEach(v => {
                            param.push({id: v.id, depot: dep.id, capacity: capacity});
                        });
                    } else {
                        dep.vehicles.forEach(v => {
                            param.push({id: v.id, depot: dep.id, capacity: v.capacity});
                        });
                    }
                });
                this.changeOrdersPerVehicle(param);
            },
            applyToAllVehicles(capacity) {
                let param = [];
                this.localData.forEach(dep => {
                    dep.vehicles.forEach(v => {
                        param.push({id: v.id, depot: dep.id, capacity: capacity});
                    });
                });
                this.changeOrdersPerVehicle(param);
            },
            loadDepotsVehicles() {
                this.localData = settings_process.loadDepotsAndVehicles(this.localVehicles, this.localDepots);
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

</style>
